def show_learn_sounds_menu(app) -> None:
    """Enter the Learn Sounds menu."""
    app.state.mode = "LEARN_SOUNDS_MENU"
    app.sounds_menu.reset_index()
    app.sounds_menu.announce_menu()


def handle_learn_sounds_menu_input(app, event, mods: int) -> None:
    """Handle Learn Sounds menu input."""
    app.sounds_menu.handle_input(event, mods)

