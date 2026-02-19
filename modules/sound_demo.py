def play_sound_demo(audio_manager, sound_type: str):
    """Play a demo sound by symbolic name from the Learn Sounds menu."""
    if sound_type == "ok":
        audio_manager.beep_ok()
    elif sound_type == "bad":
        audio_manager.beep_bad()
    elif sound_type == "progressive":
        audio_manager.play_progressive(0.5)  # 50% completion
    elif sound_type == "success":
        audio_manager.play_success()
    elif sound_type == "victory":
        audio_manager.play_victory()
    elif sound_type == "unlock":
        audio_manager.play_unlock()
    elif sound_type == "badge":
        audio_manager.play_badge()
    elif sound_type == "levelup":
        audio_manager.play_levelup()
    elif sound_type == "quest":
        audio_manager.play_quest()
    elif sound_type == "buzz":
        audio_manager.play_buzz()
    elif sound_type == "pet_robot":
        audio_manager.play_pet_sound("robot")
    elif sound_type == "pet_dragon":
        audio_manager.play_pet_sound("dragon")
    elif sound_type == "pet_owl":
        audio_manager.play_pet_sound("owl")
    elif sound_type == "pet_cat":
        audio_manager.play_pet_sound("cat")
    elif sound_type == "pet_dog":
        audio_manager.play_pet_sound("dog")
    elif sound_type == "pet_phoenix":
        audio_manager.play_pet_sound("phoenix")
    elif sound_type == "pet_tribble":
        audio_manager.play_pet_sound("tribble")
    elif sound_type == "pet_feed":
        audio_manager.play_pet_feed()
    elif sound_type == "pet_play":
        audio_manager.play_pet_play()
    elif sound_type == "pet_evolve":
        audio_manager.play_pet_evolve()

