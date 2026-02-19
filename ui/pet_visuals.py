import math
import time

import pygame


PET_PALETTES = {
    "robot": {"body": (120, 170, 220), "accent": (220, 240, 255), "detail": (60, 110, 170)},
    "dragon": {"body": (80, 170, 110), "accent": (180, 250, 170), "detail": (40, 120, 70)},
    "owl": {"body": (165, 135, 95), "accent": (240, 220, 170), "detail": (120, 90, 60)},
    "cat": {"body": (185, 130, 160), "accent": (255, 220, 240), "detail": (135, 80, 110)},
    "dog": {"body": (170, 120, 85), "accent": (230, 195, 150), "detail": (115, 80, 50)},
    "phoenix": {"body": (220, 130, 70), "accent": (255, 220, 120), "detail": (180, 80, 45)},
    "tribble": {"body": (150, 120, 190), "accent": (220, 205, 255), "detail": (105, 80, 145)},
}


def _palette_for(pet_type: str):
    return PET_PALETTES.get(pet_type, PET_PALETTES["robot"])


def _draw_base_body(surface, pet_type: str, center_x: int, center_y: int, body, detail):
    if pet_type == "robot":
        pygame.draw.rect(surface, body, (center_x - 48, center_y - 42, 96, 86), border_radius=14)
        pygame.draw.rect(surface, detail, (center_x - 32, center_y - 18, 64, 38), border_radius=8)
        pygame.draw.line(surface, detail, (center_x, center_y - 52), (center_x, center_y - 70), 4)
        pygame.draw.circle(surface, detail, (center_x, center_y - 74), 6)
        return

    if pet_type == "dragon":
        pygame.draw.ellipse(surface, body, (center_x - 55, center_y - 40, 110, 82))
        pygame.draw.polygon(
            surface,
            detail,
            [(center_x - 18, center_y - 54), (center_x, center_y - 82), (center_x + 18, center_y - 54)],
        )
        pygame.draw.polygon(
            surface,
            detail,
            [(center_x - 58, center_y - 6), (center_x - 88, center_y - 42), (center_x - 40, center_y - 26)],
        )
        pygame.draw.polygon(
            surface,
            detail,
            [(center_x + 58, center_y - 6), (center_x + 88, center_y - 42), (center_x + 40, center_y - 26)],
        )
        return

    if pet_type == "owl":
        pygame.draw.circle(surface, body, (center_x, center_y - 4), 48)
        pygame.draw.ellipse(surface, detail, (center_x - 26, center_y - 6, 52, 50))
        return

    if pet_type == "cat":
        pygame.draw.ellipse(surface, body, (center_x - 52, center_y - 38, 104, 80))
        pygame.draw.polygon(surface, detail, [(center_x - 34, center_y - 46), (center_x - 16, center_y - 82), (center_x - 2, center_y - 48)])
        pygame.draw.polygon(surface, detail, [(center_x + 34, center_y - 46), (center_x + 16, center_y - 82), (center_x + 2, center_y - 48)])
        return

    if pet_type == "dog":
        pygame.draw.ellipse(surface, body, (center_x - 54, center_y - 36, 108, 78))
        pygame.draw.ellipse(surface, detail, (center_x - 68, center_y - 26, 24, 44))
        pygame.draw.ellipse(surface, detail, (center_x + 44, center_y - 26, 24, 44))
        return

    if pet_type == "phoenix":
        pygame.draw.ellipse(surface, body, (center_x - 52, center_y - 38, 104, 80))
        pygame.draw.polygon(surface, detail, [(center_x - 20, center_y - 54), (center_x, center_y - 92), (center_x + 20, center_y - 54)])
        pygame.draw.polygon(surface, detail, [(center_x - 16, center_y + 36), (center_x, center_y + 72), (center_x + 16, center_y + 36)])
        return

    # Tribble uses a fuzzy circular silhouette with perimeter detail dots.
    pygame.draw.circle(surface, body, (center_x, center_y), 48)
    for i in range(14):
        ang = (i / 14.0) * math.pi * 2.0
        ox = int(math.cos(ang) * 44)
        oy = int(math.sin(ang) * 44)
        pygame.draw.circle(surface, detail, (center_x + ox, center_y + oy), 8)


def _draw_face(surface, mood: str, center_x: int, center_y: int, accent, detail):
    eye_y = center_y - 10
    left_eye = (center_x - 18, eye_y)
    right_eye = (center_x + 18, eye_y)

    if mood == "tired":
        pygame.draw.line(surface, detail, (left_eye[0] - 8, left_eye[1]), (left_eye[0] + 8, left_eye[1]), 3)
        pygame.draw.line(surface, detail, (right_eye[0] - 8, right_eye[1]), (right_eye[0] + 8, right_eye[1]), 3)
    elif mood == "sad":
        pygame.draw.circle(surface, detail, left_eye, 4)
        pygame.draw.circle(surface, detail, right_eye, 4)
        pygame.draw.ellipse(surface, accent, (right_eye[0] + 5, right_eye[1] + 2, 6, 10))
    elif mood == "excited":
        pygame.draw.circle(surface, accent, left_eye, 7)
        pygame.draw.circle(surface, accent, right_eye, 7)
        pygame.draw.circle(surface, detail, left_eye, 2)
        pygame.draw.circle(surface, detail, right_eye, 2)
    else:
        pygame.draw.circle(surface, accent, left_eye, 5)
        pygame.draw.circle(surface, accent, right_eye, 5)
        pygame.draw.circle(surface, detail, left_eye, 2)
        pygame.draw.circle(surface, detail, right_eye, 2)

    mouth_rect = pygame.Rect(center_x - 16, center_y + 6, 32, 16)
    if mood == "sad":
        pygame.draw.arc(surface, detail, mouth_rect.move(0, 6), math.pi, 2 * math.pi, 3)
    elif mood == "tired":
        pygame.draw.line(surface, detail, (center_x - 12, center_y + 16), (center_x + 12, center_y + 16), 3)
    elif mood == "excited":
        pygame.draw.ellipse(surface, detail, (center_x - 6, center_y + 10, 12, 10))
    else:
        pygame.draw.arc(surface, detail, mouth_rect, 0, math.pi, 3)


def _draw_stage_badges(surface, stage: int, center_x: int, base_y: int, accent, detail):
    for idx in range(5):
        color = accent if idx < stage else detail
        x = center_x - 34 + (idx * 17)
        pygame.draw.circle(surface, color, (x, base_y), 5)


def _draw_overlay(surface, mood: str, center_x: int, center_y: int, accent, t: float):
    if mood == "excited":
        for i in range(5):
            phase = t * 3.0 + i * 1.2
            x = center_x + int(math.cos(phase) * 66)
            y = center_y + int(math.sin(phase) * 56)
            pygame.draw.circle(surface, accent, (x, y), 2)
        return

    if mood == "tired":
        offset = int((t * 22) % 22)
        pygame.draw.line(surface, accent, (center_x + 52, center_y - 52 - offset), (center_x + 62, center_y - 52 - offset), 2)
        pygame.draw.line(surface, accent, (center_x + 62, center_y - 52 - offset), (center_x + 52, center_y - 40 - offset), 2)
        pygame.draw.line(surface, accent, (center_x + 52, center_y - 40 - offset), (center_x + 62, center_y - 40 - offset), 2)
        return

    if mood == "encouraging":
        pulse = 1 + int((math.sin(t * 4.0) + 1.0) * 1.5)
        pygame.draw.polygon(
            surface,
            accent,
            [(center_x, center_y - 70), (center_x - 10, center_y - 52), (center_x + 10, center_y - 52)],
            width=0,
        )
        pygame.draw.circle(surface, accent, (center_x, center_y - 76), pulse)


def _draw_item_layers(surface, center_x: int, center_y: int, item_state: dict, accent, detail):
    if not item_state:
        return

    if item_state.get("wings"):
        pygame.draw.polygon(
            surface,
            accent,
            [(center_x - 52, center_y - 18), (center_x - 102, center_y - 56), (center_x - 70, center_y + 6)],
        )
        pygame.draw.polygon(
            surface,
            accent,
            [(center_x + 52, center_y - 18), (center_x + 102, center_y - 56), (center_x + 70, center_y + 6)],
        )

    if item_state.get("hat"):
        pygame.draw.rect(surface, detail, (center_x - 34, center_y - 74, 68, 16), border_radius=6)
        pygame.draw.rect(surface, accent, (center_x - 46, center_y - 62, 92, 8), border_radius=4)

    if item_state.get("bowtie"):
        pygame.draw.polygon(surface, accent, [(center_x - 18, center_y + 24), (center_x - 2, center_y + 30), (center_x - 18, center_y + 36)])
        pygame.draw.polygon(surface, accent, [(center_x + 18, center_y + 24), (center_x + 2, center_y + 30), (center_x + 18, center_y + 36)])
        pygame.draw.circle(surface, detail, (center_x, center_y + 30), 4)

    if item_state.get("ball"):
        bx, by = center_x - 84, center_y + 58
        pygame.draw.circle(surface, accent, (bx, by), 11)
        pygame.draw.circle(surface, detail, (bx, by), 11, width=2)
        pygame.draw.line(surface, detail, (bx - 9, by), (bx + 9, by), 2)

    if item_state.get("laser"):
        lx, ly = center_x + 84, center_y + 56
        pygame.draw.rect(surface, detail, (lx - 14, ly - 4, 18, 8), border_radius=3)
        pygame.draw.line(surface, accent, (lx + 4, ly), (center_x + 20, center_y - 6), 2)
        pygame.draw.circle(surface, accent, (center_x + 20, center_y - 6), 3)

    basic_food = int(item_state.get("food_basic", 0))
    premium_food = int(item_state.get("food_premium", 0))
    if basic_food > 0 or premium_food > 0:
        fx, fy = center_x, center_y + 66
        pygame.draw.ellipse(surface, detail, (fx - 22, fy - 8, 44, 16), width=2)
        if premium_food > 0:
            pygame.draw.circle(surface, accent, (fx - 8, fy), 4)
            pygame.draw.circle(surface, accent, (fx, fy), 4)
            pygame.draw.circle(surface, accent, (fx + 8, fy), 4)
        else:
            pygame.draw.circle(surface, accent, (fx - 4, fy), 3)
            pygame.draw.circle(surface, accent, (fx + 4, fy), 3)


def draw_pet_avatar(
    *,
    screen,
    pet_type: str,
    stage: int,
    mood: str,
    center_x: int,
    center_y: int,
    panel_color,
    border_color,
    item_state=None,
):
    """Draw layered pet visuals with mood/stage overlays."""
    palette = _palette_for(pet_type)
    body = palette["body"]
    accent = palette["accent"]
    detail = palette["detail"]

    t = time.time()
    bob = int(math.sin((t * 2.0) + (hash(pet_type) % 11)) * 3)
    cy = center_y + bob

    panel_rect = pygame.Rect(center_x - 95, center_y - 95, 190, 190)
    pygame.draw.rect(screen, panel_color, panel_rect, border_radius=12)
    pygame.draw.rect(screen, border_color, panel_rect, width=2, border_radius=12)

    _draw_base_body(screen, pet_type, center_x, cy, body, detail)
    _draw_item_layers(screen, center_x, cy, item_state or {}, accent, detail)
    _draw_face(screen, mood, center_x, cy, accent, detail)
    _draw_stage_badges(screen, max(1, min(5, stage)), center_x, center_y + 78, accent, detail)
    _draw_overlay(screen, mood, center_x, cy, accent, t)
