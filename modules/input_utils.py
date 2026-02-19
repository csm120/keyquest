try:
    import pygame

    CTRL_MASK = pygame.KMOD_CTRL
except Exception:  # pragma: no cover
    pygame = None
    CTRL_MASK = 0x0040


def mod_ctrl(mods: int) -> bool:
    return (mods & CTRL_MASK) != 0

