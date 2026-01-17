extends Node
## Controller for cycling through animations in validation scenes

@export var animated_sprite: AnimatedSprite2D
@export var animation_names: Array[String] = ["idle", "walk_down", "walk_up", "walk_right", "walk_left"]
@export var time_per_animation: float = 2.0

var current_animation_index: int = 0
var timer: float = 0.0

func _ready():
	if not animated_sprite:
		animated_sprite = get_parent() as AnimatedSprite2D
	
	if animated_sprite and animated_sprite.sprite_frames:
		# Start with first animation
		if animation_names.size() > 0:
			animated_sprite.animation = animation_names[0]
			animated_sprite.play()

func _process(delta):
	if not animated_sprite or not animated_sprite.sprite_frames:
		return
	
	timer += delta
	if timer >= time_per_animation:
		timer = 0.0
		current_animation_index = (current_animation_index + 1) % animation_names.size()
		
		if current_animation_index < animation_names.size():
			var anim_name = animation_names[current_animation_index]
			if animated_sprite.sprite_frames.has_animation(anim_name):
				animated_sprite.animation = anim_name
				animated_sprite.play()
