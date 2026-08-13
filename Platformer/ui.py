import pygame
import math
from settings import (
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
)
from animal_renderer import AnimalRenderer


class Button:
    def __init__(self, rect, text, callback=None, color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, font_size=22):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.is_hovered = False
        self.scale_anim = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.callback:
                self.callback()
                return True
        return False

    def draw(self, surface):
        target_anim = 1.0 if self.is_hovered else 0.0
        self.scale_anim += (target_anim - self.scale_anim) * 0.2

        bg_col = self.hover_color if self.is_hovered else self.color

        # Cień pod przyciskiem
        shadow_rect = self.rect.move(0, 4)
        pygame.draw.rect(surface, (0, 0, 0, 90), shadow_rect, border_radius=10)

        # Animowane lekko powiększone rondo
        draw_rect = self.rect.inflate(int(self.scale_anim * 4), int(self.scale_anim * 4))
        pygame.draw.rect(surface, bg_col, draw_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255, 120), draw_rect, width=2, border_radius=10)

        txt_surf = self.font.render(self.text, True, COLOR_TEXT)
        txt_rect = txt_surf.get_rect(center=draw_rect.center)
        surface.blit(txt_surf, txt_rect)


class TextInput:
    def __init__(self, rect, default_text="Bohater", max_length=16):
        self.rect = pygame.Rect(rect)
        self.text = default_text
        self.max_length = max_length
        self.is_active = False
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.cursor_timer = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.is_active = False
            else:
                if len(self.text) < self.max_length and event.unicode.isprintable():
                    self.text += event.unicode

    def update(self, dt):
        self.cursor_timer += dt

    def draw(self, surface):
        border_col = COLOR_ACCENT if self.is_active else COLOR_PANEL_BORDER
        bg_col = (20, 16, 12) if self.is_active else (35, 28, 22)

        pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_col, self.rect, width=2 if not self.is_active else 3, border_radius=8)

        txt_surf = self.font.render(self.text if self.text else "Wpisz imię...", True, COLOR_TEXT if self.text else COLOR_TEXT_MUTED)
        txt_rect = txt_surf.get_rect(midleft=(self.rect.x + 14, self.rect.centery))
        surface.blit(txt_surf, txt_rect)

        # Mrugający kursor
        if self.is_active and int(self.cursor_timer * 2) % 2 == 0:
            cursor_x = txt_rect.right + 2 if self.text else self.rect.x + 14
            pygame.draw.line(surface, COLOR_TEXT, (cursor_x, self.rect.y + 10), (cursor_x, self.rect.bottom - 10), 2)


class CategoryTab:
    def __init__(self, rect, text, is_selected=False, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.is_selected = is_selected
        self.callback = callback
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.callback:
                self.callback()
                return True
        return False

    def draw(self, surface):
        if self.is_selected:
            bg_col = COLOR_ACCENT
            text_col = COLOR_TEXT
        elif self.is_hovered:
            bg_col = (65, 52, 40)
            text_col = COLOR_TEXT
        else:
            bg_col = COLOR_PANEL_BG
            text_col = COLOR_TEXT_MUTED

        pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, width=1, border_radius=8)

        txt_surf = self.font.render(self.text, True, text_col)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)


class AnimalCard:
    def __init__(self, rect, animal_preset, is_selected=False, callback=None):
        self.rect = pygame.Rect(rect)
        self.preset = animal_preset
        self.is_selected = is_selected
        self.callback = callback
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.is_hovered = False
        self.anim_time = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.callback:
                self.callback()
                return True
        return False

    def update(self, dt):
        self.anim_time += dt

    def draw(self, surface):
        if self.is_selected:
            bg_col = (75, 55, 35)
            border_col = COLOR_ACCENT
            border_w = 3
        elif self.is_hovered:
            bg_col = (55, 42, 32)
            border_col = COLOR_ACCENT_HOVER
            border_w = 2
        else:
            bg_col = (36, 28, 22)
            border_col = COLOR_PANEL_BORDER
            border_w = 1

        pygame.draw.rect(surface, bg_col, self.rect, border_radius=10)
        pygame.draw.rect(surface, border_col, self.rect, width=border_w, border_radius=10)

        # Minaturka zwierzaka
        icon_x = self.rect.centerx
        icon_y = self.rect.y + 36
        AnimalRenderer.render(
            surface,
            icon_x,
            icon_y,
            self.preset["id"],
            scale=0.6,
            anim_time=self.anim_time,
            is_moving=False,
        )

        # Nazwa gatunku
        name_surf = self.font.render(self.preset["name"], True, COLOR_TEXT if (self.is_selected or self.is_hovered) else COLOR_TEXT_MUTED)
        name_rect = name_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 16))
        surface.blit(name_surf, name_rect)


class ColorSwatchPicker:
    def __init__(self, x, y, label, default_color, on_color_change=None):
        self.x = x
        self.y = y
        self.label = label
        self.current_color = default_color
        self.on_color_change = on_color_change
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

        # Paleta 8 gotowych kolorów
        self.colors = [
            (220, 90, 40),   # Lisia czerwień
            (240, 160, 60),  # Złoty/Rudy
            (235, 220, 205), # Kremowy
            (130, 135, 145), # Szary
            (95, 60, 35),    # Ciemny brąz
            (90, 190, 70),   # Zielony
            (100, 160, 210), # Niebieski
            (245, 170, 210), # Różowy
        ]
        self.swatch_rects = []
        for i, c in enumerate(self.colors):
            rx = x + 100 + (i % 4) * 32
            ry = y + (i // 4) * 32
            self.swatch_rects.append((pygame.Rect(rx, ry, 26, 26), c))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, col in self.swatch_rects:
                if rect.collidepoint(event.pos):
                    self.current_color = col
                    if self.on_color_change:
                        self.on_color_change(col)
                    return True
        return False

    def draw(self, surface):
        lbl_surf = self.font.render(self.label, True, COLOR_TEXT)
        surface.blit(lbl_surf, (self.x, self.y + 6))

        for rect, col in self.swatch_rects:
            is_selected = (col == self.current_color)
            pygame.draw.rect(surface, col, rect, border_radius=6)
            b_col = COLOR_ACCENT if is_selected else COLOR_PANEL_BORDER
            pygame.draw.rect(surface, b_col, rect, width=3 if is_selected else 1, border_radius=6)
