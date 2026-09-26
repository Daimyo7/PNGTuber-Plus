extends Node2D

@onready var buttonScene = preload("res://ui_scenes/microphoneSelect/mic_select_button.tscn")
@onready var container = $ScrollContainer/VBoxContainer

func _ready():
	visibility_changed.connect(_on_visibility_changed)
	if visible:
		showMicMenu()

func _on_visibility_changed():
	if visible:
		showMicMenu()

func showMicMenu():
	for child in container.get_children():
		child.free()
	
	var inputList = AudioServer.get_input_device_list()
	for input in inputList:
		var newButton = buttonScene.instantiate()
		newButton.micName = input
		container.add_child(newButton)
