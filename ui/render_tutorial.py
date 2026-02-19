from ui.a11y import draw_controls_hint, draw_focus_frame


def _tutorial_keyset(tutorial_state, tutorial_data):
    if tutorial_state.phase == 1:
        return tutorial_data.PHASE1_KEYS
    if tutorial_state.phase == 2:
        return tutorial_data.PHASE2_INTRO_KEYS
    if tutorial_state.phase == 3:
        return tutorial_data.PHASE3_INTRO_KEYS
    if tutorial_state.phase == 4:
        return tutorial_data.PHASE4_INTRO_KEYS
    return tutorial_data.PHASE4_MIX_KEYS


def draw_tutorial_screen(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    wrap_text,
    screen_w: int,
    fg,
    accent,
    hilite,
    tutorial_state,
    tutorial_data,
):
    if tutorial_state.in_intro:
        title = f"Tutorial Key Guide (Phase {tutorial_state.phase})"
        title_surf, _ = title_font.render(title, accent)
        screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 70))

        if tutorial_state.intro_items:
            name, desc = tutorial_state.intro_items[tutorial_state.intro_index]
            header = f"{tutorial_data.FRIENDLY.get(name, name)} ({tutorial_state.intro_index + 1}/{len(tutorial_state.intro_items)})"
            header_surf, _ = text_font.render(header, fg)
            screen.blit(header_surf, (screen_w // 2 - header_surf.get_width() // 2, 140))

            y = 200
            for line in wrap_text(desc, screen_w - 120):
                line_surf, _ = small_font.render(line, fg)
                screen.blit(line_surf, (screen_w // 2 - line_surf.get_width() // 2, y))
                y += 30

        draw_controls_hint(
            screen=screen,
            small_font=small_font,
            text="Up/Down review keys; Ctrl+Space repeat; Enter/Space start practice; Esc menu",
            screen_w=screen_w,
            y=540,
            accent=accent,
        )
        return

    prompt = f"Press {tutorial_data.FRIENDLY[tutorial_state.required_name]}"
    prompt_label_surf, _ = text_font.render("Type now:", accent)
    screen.blit(prompt_label_surf, (screen_w // 2 - prompt_label_surf.get_width() // 2, 65))
    prompt_surf, _ = title_font.render(prompt, fg)
    prompt_rect = prompt_surf.get_rect(topleft=(screen_w // 2 - prompt_surf.get_width() // 2, 100))
    screen.blit(prompt_surf, prompt_rect)
    draw_focus_frame(screen, prompt_rect, hilite, accent)

    y = 200
    keyset = _tutorial_keyset(tutorial_state, tutorial_data)

    for name, _key in keyset:
        cnt = tutorial_state.counts_done.get(name, 0)
        total = tutorial_state.target_counts.get(name, tutorial_data.TUTORIAL_EACH_COUNT)
        lbl = f"{tutorial_data.FRIENDLY[name]}: {cnt}/{total}"
        surf, _ = text_font.render(lbl, fg)
        screen.blit(surf, (screen_w // 2 - surf.get_width() // 2, y))
        y += 40

    if tutorial_state.guidance_message:
        y += 20
        for line in wrap_text(tutorial_state.guidance_message, screen_w - 80):
            guide_surf, _ = text_font.render(line, hilite)
            screen.blit(guide_surf, (screen_w // 2 - guide_surf.get_width() // 2, y))
            y += 35

    if tutorial_state.hint_message:
        y += 10
        for line in wrap_text(tutorial_state.hint_message, screen_w - 80):
            hint_surf, _ = small_font.render(line, accent)
            screen.blit(hint_surf, (screen_w // 2 - hint_surf.get_width() // 2, y))
            y += 28

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Ctrl+Space repeat; Esc menu",
        screen_w=screen_w,
        y=y + 40,
        accent=accent,
    )
