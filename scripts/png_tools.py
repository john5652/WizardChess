#!/usr/bin/env python3
"""
Minimal PNG reader/writer + background-to-alpha cleanup.

Why this exists:
- No external deps (Pillow/ImageMagick) in this environment.
- Several project assets appear to have a "checkerboard" baked into pixels.
  Those PNGs are RGB (no alpha), so Godot will render the checkerboard.

This module supports:
- Non-interlaced PNG
- 8-bit truecolor (RGB) and truecolor+alpha (RGBA)
- Filters 0-4
"""

from __future__ import annotations

import struct
import zlib
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class PngImage:
	width: int
	height: int
	# Always stored as RGBA bytes (len = width * height * 4)
	rgba: bytes


def _read_chunks(png_bytes: bytes) -> Iterable[Tuple[bytes, bytes]]:
	# yields (type, data)
	if not png_bytes.startswith(PNG_SIGNATURE):
		raise ValueError("Not a PNG (bad signature)")
	i = len(PNG_SIGNATURE)
	while i < len(png_bytes):
		if i + 8 > len(png_bytes):
			break
		length = struct.unpack(">I", png_bytes[i : i + 4])[0]
		chunk_type = png_bytes[i + 4 : i + 8]
		i += 8
		data = png_bytes[i : i + length]
		i += length
		# crc = png_bytes[i : i + 4]
		i += 4
		yield (chunk_type, data)
		if chunk_type == b"IEND":
			break


def _paeth(a: int, b: int, c: int) -> int:
	p = a + b - c
	pa = abs(p - a)
	pb = abs(p - b)
	pc = abs(p - c)
	if pa <= pb and pa <= pc:
		return a
	if pb <= pc:
		return b
	return c


def _unfilter_scanlines(
	raw: bytes, width: int, height: int, bpp: int
) -> bytes:
	"""
	raw is the decompressed IDAT stream, which is `height` scanlines of:
	  filter_type (1 byte) + scanline_bytes (width * bpp bytes)
	Returns concatenated scanline_bytes for all rows (no filter bytes).
	"""
	row_bytes = width * bpp
	stride = 1 + row_bytes
	expected = height * stride
	if len(raw) < expected:
		raise ValueError(f"IDAT too small: got {len(raw)} expected {expected}")

	out = bytearray(height * row_bytes)
	for y in range(height):
		row_start = y * stride
		filt = raw[row_start]
		src = raw[row_start + 1 : row_start + 1 + row_bytes]
		dst_off = y * row_bytes

		if filt == 0:
			out[dst_off : dst_off + row_bytes] = src
			continue

		for x in range(row_bytes):
			left = out[dst_off + x - bpp] if x >= bpp else 0
			up = out[dst_off - row_bytes + x] if y > 0 else 0
			up_left = out[dst_off - row_bytes + x - bpp] if (y > 0 and x >= bpp) else 0

			val = src[x]
			if filt == 1:  # Sub
				out[dst_off + x] = (val + left) & 0xFF
			elif filt == 2:  # Up
				out[dst_off + x] = (val + up) & 0xFF
			elif filt == 3:  # Average
				out[dst_off + x] = (val + ((left + up) // 2)) & 0xFF
			elif filt == 4:  # Paeth
				out[dst_off + x] = (val + _paeth(left, up, up_left)) & 0xFF
			else:
				raise ValueError(f"Unsupported PNG filter: {filt}")
	return bytes(out)


def read_png(path: str) -> PngImage:
	with open(path, "rb") as f:
		png = f.read()

	ihdr = None
	idat_parts: List[bytes] = []
	for ctype, data in _read_chunks(png):
		if ctype == b"IHDR":
			ihdr = data
		elif ctype == b"IDAT":
			idat_parts.append(data)
		elif ctype == b"IEND":
			break

	if ihdr is None:
		raise ValueError("PNG missing IHDR")

	width, height, bit_depth, color_type, comp, filt, interlace = struct.unpack(
		">IIBBBBB", ihdr
	)
	if comp != 0 or filt != 0:
		raise ValueError("Unsupported PNG compression/filter method")
	if interlace != 0:
		raise ValueError("Interlaced PNG not supported")
	if bit_depth != 8:
		raise ValueError("Only 8-bit PNG supported")

	# Truecolor (2) or Truecolor+Alpha (6)
	if color_type == 2:
		bpp = 3
	elif color_type == 6:
		bpp = 4
	else:
		raise ValueError(f"Unsupported PNG color type: {color_type}")

	raw = zlib.decompress(b"".join(idat_parts))
	pixels = _unfilter_scanlines(raw, width, height, bpp=bpp)

	if bpp == 4:
		rgba = pixels
	else:
		# expand RGB -> RGBA
		rgba_out = bytearray(width * height * 4)
		for i in range(width * height):
			rgba_out[i * 4 + 0] = pixels[i * 3 + 0]
			rgba_out[i * 4 + 1] = pixels[i * 3 + 1]
			rgba_out[i * 4 + 2] = pixels[i * 3 + 2]
			rgba_out[i * 4 + 3] = 255
		rgba = bytes(rgba_out)

	return PngImage(width=width, height=height, rgba=rgba)


def _filter_none_rgba(rgba: bytes, width: int, height: int) -> bytes:
	# emit scanlines with filter byte 0 + raw RGBA
	row_bytes = width * 4
	out = bytearray(height * (1 + row_bytes))
	for y in range(height):
		out[y * (1 + row_bytes)] = 0
		start = y * row_bytes
		out[y * (1 + row_bytes) + 1 : y * (1 + row_bytes) + 1 + row_bytes] = rgba[
			start : start + row_bytes
		]
	return bytes(out)


def write_png_rgba(path: str, img: PngImage) -> None:
	# Uses color_type=6 (RGBA), filter method 0, compression deflate.
	ihdr = struct.pack(">IIBBBBB", img.width, img.height, 8, 6, 0, 0, 0)

	def chunk(ctype: bytes, data: bytes) -> bytes:
		crc = zlib.crc32(ctype + data) & 0xFFFFFFFF
		return struct.pack(">I", len(data)) + ctype + data + struct.pack(">I", crc)

	raw_scanlines = _filter_none_rgba(img.rgba, img.width, img.height)
	compressed = zlib.compress(raw_scanlines, level=6)

	out = bytearray()
	out += PNG_SIGNATURE
	out += chunk(b"IHDR", ihdr)
	out += chunk(b"IDAT", compressed)
	out += chunk(b"IEND", b"")

	with open(path, "wb") as f:
		f.write(out)


def _color_dist_sq(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
	return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def _sample_border_colors(img: PngImage, step: int = 16) -> List[Tuple[int, int, int]]:
	w, h = img.width, img.height
	rgba = img.rgba
	colors: List[Tuple[int, int, int]] = []

	def get_rgb(x: int, y: int) -> Tuple[int, int, int]:
		i = (y * w + x) * 4
		return (rgba[i], rgba[i + 1], rgba[i + 2])

	# Sample edges
	for x in range(0, w, step):
		colors.append(get_rgb(x, 0))
		colors.append(get_rgb(x, h - 1))
	for y in range(0, h, step):
		colors.append(get_rgb(0, y))
		colors.append(get_rgb(w - 1, y))
	return colors


def background_to_alpha_floodfill(
	img: PngImage,
	tolerance: int = 28,
	max_seed_colors: int = 2,
) -> PngImage:
	"""
	Convert background connected to image borders into alpha=0 using flood fill.

	- Seeds are the most common border colors (top N).
	- Only pixels connected to the border and "close enough" to a seed color are removed.
	"""
	w, h = img.width, img.height
	rgba = bytearray(img.rgba)

	border_colors = _sample_border_colors(img, step=16)
	common = Counter(border_colors).most_common(max_seed_colors)
	seeds = [c for c, _ in common]
	if not seeds:
		return img

	tol_sq = tolerance * tolerance

	def is_bg(rgb: Tuple[int, int, int]) -> bool:
		return any(_color_dist_sq(rgb, s) <= tol_sq for s in seeds)

	visited = bytearray(w * h)
	qx: List[int] = []
	qy: List[int] = []

	def push(x: int, y: int) -> None:
		idx = y * w + x
		if visited[idx]:
			return
		visited[idx] = 1
		qx.append(x)
		qy.append(y)

	# Seed with all border pixels that match background
	for x in range(w):
		push(x, 0)
		push(x, h - 1)
	for y in range(h):
		push(0, y)
		push(w - 1, y)

	while qx:
		x = qx.pop()
		y = qy.pop()
		i = (y * w + x) * 4
		rgb = (rgba[i], rgba[i + 1], rgba[i + 2])
		if not is_bg(rgb):
			continue

		# Make transparent
		rgba[i + 3] = 0

		# 4-neighbors
		if x > 0:
			push(x - 1, y)
		if x + 1 < w:
			push(x + 1, y)
		if y > 0:
			push(x, y - 1)
		if y + 1 < h:
			push(x, y + 1)

	return PngImage(width=w, height=h, rgba=bytes(rgba))

