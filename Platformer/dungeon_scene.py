import pygame
import math
import random
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT,
    COLOR_ACCENT,
    COLOR_SUCCESS,
)
from ui import Button

# Definicje różnych Bossów od Poziomu 1 do 5+
BOSS_PRESETS = [
    {
        "level": 1,
        "name": "Mroczny Smok Cienia",
        "max_hp": 800,
        "color_body": (35, 25, 45),
        "color_core": (80, 30, 90),
        "color_horn": (200, 40, 60),
        "color_eye": (255, 40, 60),
        "color_bullet": (230, 40, 70),
        "bullet_count": 5,
        "bullet_speed": 240,
        "cooldown_min": 1.5,
        "cooldown_max": 2.2,
        "wings_style": "shadow",
    },
    {
        "level": 2,
        "name": "Płomienny Demon Wulkanu",
        "max_hp": 1300,
        "color_body": (80, 20, 10),
        "color_core": (240, 90, 20),
        "color_horn": (255, 200, 40),
        "color_eye": (255, 140, 20),
        "color_bullet": (255, 100, 20),
        "bullet_count": 7,
        "bullet_speed": 280,
        "cooldown_min": 1.1,
        "cooldown_max": 1.8,
        "wings_style": "fire",
    },
    {
        "level": 3,
        "name": "Lodowy Władca Mrozu",
        "max_hp": 1900,
        "color_body": (20, 50, 80),
        "color_core": (60, 180, 240),
        "color_horn": (180, 240, 255),
        "color_eye": (100, 240, 255),
        "color_bullet": (120, 220, 255),
        "bullet_count": 9,
        "bullet_speed": 320,
        "cooldown_min": 0.9,
        "cooldown_max": 1.5,
        "wings_style": "ice",
    },
    {
        "level": 4,
        "name": "Pożeracz Dusz Chaosu",
        "max_hp": 2600,
        "color_body": (15, 10, 25),
        "color_core": (160, 40, 220),
        "color_horn": (220, 100, 255),
        "color_eye": (230, 80, 255),
        "color_bullet": (200, 50, 250),
        "bullet_count": 12,
        "bullet_speed": 360,
        "cooldown_min": 0.7,
        "cooldown_max": 1.2,
        "wings_style": "void",
    },
    {
        "level": 5,
        "name": "Złoty Archont Światłości i Cienia",
        "max_hp": 3500,
        "color_body": (240, 190, 40),
        "color_core": (255, 245, 180),
        "color_horn": (255, 255, 255),
        "color_eye": (255, 220, 80),
        "color_bullet": (255, 215, 60),
        "bullet_count": 16,
        "bullet_speed": 400,
        "cooldown_min": 0.5,
        "cooldown_max": 1.0,
        "wings_style": "gold",
    },
]


class Boss:
    """Boss Lochów dostosowujący wygląd i trudność do poziomu wyzwania."""

    def __init__(self, x, y, boss_level=1):
        self.x = float(x)
        self.y = float(y)
        self.boss_level = boss_level

        # Wybór konfiguracji z listy
        idx = min(boss_level - 1, len(BOSS_PRESETS) - 1)
        self.config = BOSS_PRESETS[idx]

        # Wzrost HP dla wyższych poziomów
        bonus_hp = (boss_level - len(BOSS_PRESETS)) * 800 if boss_level > len(BOSS_PRESETS) else 0
        self.max_hp = self.config["max_hp"] + bonus_hp
        self.hp = self.max_hp
        self.name = f"{self.config['name']} [Poziom {self.boss_level}]"

        self.attack_cooldown = 1.5
        self.anim_time = 0.0
        self.is_enraged = False
        self.projectiles = []
        self.shockwaves = []

    def update(self, dt, player_pos):
        self.anim_time += dt
        self.attack_cooldown -= dt

        # Szał poniżej 50% HP
        self.is_enraged = (self.hp <= self.max_hp // 2)

        if self.attack_cooldown <= 0:
            cd_min = self.config["cooldown_min"] * (0.7 if self.is_enraged else 1.0)
            cd_max = self.config["cooldown_max"] * (0.7 if self.is_enraged else 1.0)
            self.attack_cooldown = random.uniform(cd_min, cd_max)

            num_bullets = self.config["bullet_count"] + (3 if self.is_enraged else 0)
            bullet_speed = self.config["bullet_speed"] + (40 if self.is_enraged else 0)
            spread = 0.8 + (0.3 if self.is_enraged else 0.0)

            # Fala uderzeniowa
            if self.is_enraged or self.boss_level >= 2:
                self.shockwaves.append({"radius": 20, "max_radius": 240, "life": 1.2})

            base_ang = math.atan2(player_pos[1] - self.y, player_pos[0] - self.x)
            for i in range(num_bullets):
                ang = base_ang + (i - (num_bullets - 1) / 2) * (spread / num_bullets)
                self.projectiles.append({
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(ang) * bullet_speed,
                    "vy": math.sin(ang) * bullet_speed,
                    "radius": 14 if self.is_enraged else 12,
                    "life": 3.2
                })

        # Aktualizacja pocisków
        for proj in self.projectiles[:]:
            proj["x"] += proj["vx"] * dt
            proj["y"] += proj["vy"] * dt
            proj["life"] -= dt
            if proj["life"] <= 0:
                self.projectiles.remove(proj)

        # Aktualizacja fal uderzeniowych
        for sw in self.shockwaves[:]:
            sw["radius"] += 200 * dt
            sw["life"] -= dt
            if sw["life"] <= 0 or sw["radius"] >= sw["max_radius"]:
                self.shockwaves.remove(sw)

    def draw(self, surface):
        bob = math.sin(self.anim_time * (7 if self.is_enraged else 4)) * 9
        bx = int(self.x)
        by = int(self.y + bob)

        # Aura Bossa zależna od gatunku
        if self.is_enraged:
            aura_r = int(80 + math.sin(self.anim_time * 14) * 12)
            pygame.draw.circle(surface, self.config["color_bullet"], (bx, by), aura_r, width=3)

        # Cień pod Bossem
        pygame.draw.ellipse(surface, (0, 0, 0, 140), (bx - 80, by + 45, 160, 34))

        # Skrzydła Bossa
        w_speed = 8 if self.is_enraged else 4
        w_flap = math.sin(self.anim_time * w_speed) * 22
        w_col = self.config["color_body"]

        pygame.draw.polygon(surface, w_col, [(bx - 30, by - 10), (bx - 140, by - 90 + w_flap), (bx - 75, by + 38)])
        pygame.draw.polygon(surface, w_col, [(bx + 30, by - 10), (bx + 140, by - 90 + w_flap), (bx + 75, by + 38)])

        # Korona / Aureola (dla Złotego Archonta i wysokich bossów)
        if self.config["wings_style"] == "gold":
            pygame.draw.circle(surface, (255, 235, 120), (bx, by - 65), 24, width=4)

        # Ciało i Rdzeń
        pygame.draw.circle(surface, self.config["color_body"], (bx, by), 64)
        pygame.draw.circle(surface, self.config["color_core"], (bx, by), 50)

        # Głowa i Rogi
        pygame.draw.circle(surface, (25, 18, 32), (bx, by - 44), 42)
        pygame.draw.line(surface, self.config["color_horn"], (bx - 24, by - 64), (bx - 55, by - 105), 10)
        pygame.draw.line(surface, self.config["color_horn"], (bx + 24, by - 64), (bx + 55, by - 105), 10)

        # Świecące Oczy
        e_col = self.config["color_eye"]
        pygame.draw.circle(surface, e_col, (int(bx - 16), int(by - 48)), 9)
        pygame.draw.circle(surface, e_col, (int(bx + 16), int(by - 48)), 9)
        pygame.draw.circle(surface, (255, 255, 255), (int(bx - 16), int(by - 48)), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(bx + 16), int(by - 48)), 4)

        # Fale uderzeniowe
        for sw in self.shockwaves:
            pygame.draw.circle(surface, self.config["color_bullet"], (bx, by), int(sw["radius"]), width=4)

        # Pociski Bossa
        for proj in self.projectiles:
            pygame.draw.circle(surface, self.config["color_bullet"], (int(proj["x"]), int(proj["y"])), proj["radius"])
            pygame.draw.circle(surface, (255, 255, 255), (int(proj["x"]), int(proj["y"])), proj["radius"] // 2)


class DungeonScene:
    """Scena Lochu z dynamicznym doborem Bossa i poziomem trudności."""

    def __init__(self, player, sound_manager, on_victory_cb):
        self.player = player
        self.sound_manager = sound_manager
        self.on_victory_cb = on_victory_cb

        self.font_title = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_ui = pygame.font.SysFont("Arial", 16, bold=True)

        self.boss_level = 1
        self.boss = Boss(SCREEN_WIDTH // 2, 210, boss_level=self.boss_level)
        self.player_projectiles = []

        self.player_damage = 25
        self.game_over = False
        self.victory = False

        self.btn_return = Button(
            (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 80, 240, 48),
            "Powrót do Gniazda",
            callback=self._finish_battle,
            color=COLOR_ACCENT,
            font_size=18,
        )
        self.anim_time = 0.0

    def start_dungeon(self):
        self.boss = Boss(SCREEN_WIDTH // 2, 210, boss_level=self.boss_level)
        self.player.x = SCREEN_WIDTH // 2
        self.player.y = SCREEN_HEIGHT - 130
        self.player_projectiles = []
        self.game_over = False
        self.victory = False
        self.player_damage = self.player.calc_combat_stats()

    def _finish_battle(self):
        if self.victory:
            self.boss_level += 1  # Awans na kolejnego, silniejszego bossa z nowym wyglądem!
        if self.on_victory_cb:
            self.on_victory_cb()

    def handle_event(self, event):
        if (self.game_over or self.victory):
            self.btn_return.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_j:
                self._player_attack()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._player_attack()

    def _player_attack(self):
        if self.player.attack_cooldown <= 0:
            self.player.attack_cooldown = 0.22
            self.sound_manager.play("eat")

            ang = math.atan2(self.boss.y - self.player.y, self.boss.x - self.player.x)
            self.player_projectiles.append({
                "x": self.player.x,
                "y": self.player.y - 20,
                "vx": math.cos(ang) * 480,
                "vy": math.sin(ang) * 480,
                "radius": 11,
                "life": 2.0
            })

    def update(self, dt, keys):
        self.anim_time += dt

        if self.game_over or self.victory:
            return

        self.player.handle_input(keys, dt)
        self.player.x = max(120, min(SCREEN_WIDTH - 120, self.player.x))
        self.player.y = max(180, min(SCREEN_HEIGHT - 80, self.player.y))

        if self.player.attack_cooldown > 0:
            self.player.attack_cooldown -= dt

        self.boss.update(dt, (self.player.x, self.player.y))

        # Pociski gracza
        for proj in self.player_projectiles[:]:
            proj["x"] += proj["vx"] * dt
            proj["y"] += proj["vy"] * dt
            proj["life"] -= dt

            if math.hypot(proj["x"] - self.boss.x, proj["y"] - self.boss.y) < 60:
                self.boss.hp -= self.player_damage
                self.sound_manager.play("click")
                if proj in self.player_projectiles:
                    self.player_projectiles.remove(proj)

                if self.boss.hp <= 0:
                    self.boss.hp = 0
                    self.victory = True
                    self.sound_manager.play("mirror")
            elif proj["life"] <= 0 and proj in self.player_projectiles:
                self.player_projectiles.remove(proj)

        # Pociski Bossa
        p_pos = (self.player.x, self.player.y)
        for proj in self.boss.projectiles[:]:
            if math.hypot(proj["x"] - p_pos[0], proj["y"] - p_pos[1]) < 24:
                self.player.hp -= 24
                self.sound_manager.play("step")
                if proj in self.boss.projectiles:
                    self.boss.projectiles.remove(proj)

                if self.player.hp <= 0:
                    self.player.hp = 0
                    self.game_over = True

        # Fale uderzeniowe
        for sw in self.boss.shockwaves:
            dist_sw = math.hypot(self.boss.x - p_pos[0], self.boss.y - p_pos[1])
            if abs(dist_sw - sw["radius"]) < 20:
                self.player.hp -= 22
                self.sound_manager.play("step")
                if self.player.hp <= 0:
                    self.player.hp = 0
                    self.game_over = True

    def draw(self, surface):
        surface.fill((16, 12, 18))

        floor_rect = pygame.Rect(80, 100, SCREEN_WIDTH - 160, SCREEN_HEIGHT - 140)
        pygame.draw.rect(surface, (32, 26, 36), floor_rect, border_radius=16)
        pygame.draw.rect(surface, (60, 45, 65), floor_rect, width=4, border_radius=16)

        # Pochodnie
        for ty in [180, 340, 500]:
            for tx in [100, SCREEN_WIDTH - 100]:
                pygame.draw.rect(surface, (90, 60, 40), (tx - 6, ty, 12, 24))
                flame_glow = int(200 + math.sin(self.anim_time * 10 + ty) * 45)
                pygame.draw.circle(surface, (flame_glow, 120, 30), (tx, ty - 6), 10)

        # Rysowanie Bossa
        self.boss.draw(surface)

        # Pociski Gracza
        for proj in self.player_projectiles:
            pygame.draw.circle(surface, (100, 220, 255), (int(proj["x"]), int(proj["y"])), proj["radius"])
            pygame.draw.circle(surface, (255, 255, 255), (int(proj["x"]), int(proj["y"])), proj["radius"] // 2)

        # Rysowanie Gracza
        self.player.draw(surface)

        # --- HUD WALKI ---
        boss_bar_w = 460
        boss_bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - boss_bar_w // 2, 20, boss_bar_w, 24)
        pygame.draw.rect(surface, (30, 20, 25), boss_bar_rect, border_radius=6)
        fill_w = int((max(0, self.boss.hp) / self.boss.max_hp) * boss_bar_w)
        if fill_w > 0:
            pygame.draw.rect(surface, (220, 45, 65), (boss_bar_rect.x, boss_bar_rect.y, fill_w, 24), border_radius=6)
        pygame.draw.rect(surface, (245, 195, 60), boss_bar_rect, width=2, border_radius=6)

        b_txt = self.font_ui.render(f"{self.boss.name}: {self.boss.hp}/{self.boss.max_hp} HP", True, COLOR_TEXT)
        surface.blit(b_txt, (boss_bar_rect.centerx - b_txt.get_width() // 2, boss_bar_rect.y + 4))

        # Pasek Zdrowia Gracza (Baza 350 HP!)
        p_bar_w = 280
        p_bar_rect = pygame.Rect(40, SCREEN_HEIGHT - 45, p_bar_w, 20)
        pygame.draw.rect(surface, (30, 20, 25), p_bar_rect, border_radius=6)
        p_fill = int((max(0, self.player.hp) / self.player.max_hp) * p_bar_w)
        if p_fill > 0:
            pygame.draw.rect(surface, (60, 190, 90), (p_bar_rect.x, p_bar_rect.y, p_fill, 20), border_radius=6)
        pygame.draw.rect(surface, COLOR_ACCENT, p_bar_rect, width=2, border_radius=6)

        p_txt = self.font_ui.render(f"HP Gracza: {self.player.hp}/{self.player.max_hp} | Obrażenia: {self.player_damage}", True, COLOR_TEXT)
        surface.blit(p_txt, (p_bar_rect.x, p_bar_rect.y - 22))

        ctrl_txt = self.font_ui.render("Sterowanie: [SPACJA / Kliknięcie Myszki] - Atak Magiczny Mocy", True, COLOR_ACCENT)
        surface.blit(ctrl_txt, (SCREEN_WIDTH - ctrl_txt.get_width() - 40, SCREEN_HEIGHT - 35))

        # Ekran końcowy
        if self.victory or self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 140, 440, 260)
            pygame.draw.rect(surface, (35, 28, 22), card_rect, border_radius=14)
            pygame.draw.rect(surface, COLOR_ACCENT, card_rect, width=3, border_radius=14)

            if self.victory:
                res_title = self.font_title.render("TRIUMFALNE ZWYCIĘSTWO!", True, (255, 215, 60))
                res_sub = self.font_ui.render(f"Pokonano {self.boss.name}!", True, COLOR_TEXT)
                res_pts = self.font_ui.render(f"Kolejne wyzwanie: Boss Poziomu {self.boss_level + 1}!", True, COLOR_SUCCESS)
            else:
                res_title = self.font_title.render("PORAŻKA W LOCHU!", True, (240, 60, 70))
                res_sub = self.font_ui.render(f"{self.boss.name} okazał się zbyt potężny...", True, COLOR_TEXT)
                res_pts = self.font_ui.render("Zbierz więcej jedzenia na arenie przy następnej próbie!", True, COLOR_ACCENT)

            surface.blit(res_title, (card_rect.centerx - res_title.get_width() // 2, card_rect.y + 25))
            surface.blit(res_sub, (card_rect.centerx - res_sub.get_width() // 2, card_rect.y + 70))
            surface.blit(res_pts, (card_rect.centerx - res_pts.get_width() // 2, card_rect.y + 105))

            self.btn_return.draw(surface)
