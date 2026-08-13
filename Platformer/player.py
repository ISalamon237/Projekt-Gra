import pygame
import math
from settings import PLAYER_SPEED, COLOR_TEXT, COLOR_ACCENT
from animal_renderer import AnimalRenderer
from animal_presets import ANIMAL_BY_ID


class Player(pygame.sprite.Sprite):
    """Klasa Gracza reprezentująca spersonalizowaną postać zwierzęcia."""

    def __init__(self, x, y, name="Bohater", animal_id="fox"):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.name = name
        self.animal_id = animal_id
        
        # Pobranie barw z wybranego gatunku jako domyślne
        preset = ANIMAL_BY_ID.get(animal_id, ANIMAL_BY_ID["fox"])
        self.color_body = preset["color_body"]
        self.color_accent = preset["color_accent"]
        self.color_eye = preset["color_eye"]
        self.accessory = "Brak"

        self.power_points = 0
        self.max_hp = 350
        self.hp = 350
        self.attack_cooldown = 0.0

        self.speed = PLAYER_SPEED
        self.speed_boost_timer = 0.0
        self.direction = "down"
        self.is_moving = False
        self.anim_time = 0.0
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

        # Prostokąt kolizji (dół postaci)
        self.rect = pygame.Rect(int(self.x - 16), int(self.y - 10), 32, 24)

    def reset_challenge(self):
        self.power_points = 0
        self.max_hp = 350
        self.hp = 350
        self.speed_boost_timer = 0.0

    def calc_combat_stats(self):
        # Im więcej zgromadzonej mocy z jedzenia, tym większe HP i obrażenia gracza!
        bonus_hp = self.power_points // 2
        self.max_hp = 350 + bonus_hp
        self.hp = self.max_hp
        base_damage = 25 + (self.power_points // 10)
        return base_damage



    def customize(self, name, animal_id, color_body, color_accent, color_eye, accessory):
        self.name = name
        self.animal_id = animal_id
        self.color_body = color_body
        self.color_accent = color_accent
        self.color_eye = color_eye
        self.accessory = accessory

    def handle_input(self, keys, dt, obstacles=None):
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # Zwiększona prędkość jeśli zjedzono przysmak
        current_speed = self.speed * (1.4 if self.speed_boost_timer > 0 else 1.0)
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt

        if dx != 0 and dy != 0:
            # Normalizacja wektora przekątnej
            dx *= 0.7071
            dy *= 0.7071

        self.is_moving = (dx != 0 or dy != 0)

        if self.is_moving:
            self.anim_time += dt
            if dx < 0:
                self.direction = "left"
            elif dx > 0:
                self.direction = "right"
            elif dy < 0:
                self.direction = "up"
            elif dy > 0:
                self.direction = "down"

            # Próba ruchu X
            new_x = self.x + dx * current_speed
            temp_rect = pygame.Rect(int(new_x - 16), int(self.y - 10), 32, 24)
            if not obstacles or not any(temp_rect.colliderect(obs) for obs in obstacles):
                self.x = new_x

            # Próba ruchu Y
            new_y = self.y + dy * current_speed
            temp_rect = pygame.Rect(int(self.x - 16), int(new_y - 10), 32, 24)
            if not obstacles or not any(temp_rect.colliderect(obs) for obs in obstacles):
                self.y = new_y

            self.rect.topleft = (int(self.x - 16), int(self.y - 10))
        else:
            self.anim_time += dt * 0.5

    def update(self, dt):
        pass

    def draw(self, surface, camera_offset=(0, 0)):
        draw_x = self.x - camera_offset[0]
        draw_y = self.y - camera_offset[1]

        # Rysowanie postaci zwierzątka
        AnimalRenderer.render(
            surface,
            draw_x,
            draw_y,
            self.animal_id,
            color_body=self.color_body,
            color_accent=self.color_accent,
            color_eye=self.color_eye,
            accessory=self.accessory,
            scale=1.1,
            anim_time=self.anim_time,
            is_moving=self.is_moving,
            direction=self.direction,
        )

        # Tabliczka z imieniem nad głową
        name_surf = self.font.render(self.name, True, COLOR_TEXT)
        badge_w = name_surf.get_width() + 12
        badge_h = name_surf.get_height() + 4
        badge_rect = pygame.Rect(draw_x - badge_w // 2, draw_y - 52, badge_w, badge_h)

        # Tło tabliczki
        pygame.draw.rect(surface, (20, 16, 12, 200), badge_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_ACCENT, badge_rect, width=1, border_radius=6)

        name_rect = name_surf.get_rect(center=badge_rect.center)
        surface.blit(name_surf, name_rect)
