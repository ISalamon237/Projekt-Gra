import pygame
import math
import random
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT,
    COLOR_SUCCESS,
    ARENA_DURATION,
    RUSH_DURATION,
)
from animal_presets import ANIMAL_PRESETS
from animal_renderer import AnimalRenderer
from ui import Button


class FoodItem:
    """Jedzenie na arenie dające +10 punktów mocy."""

    FOOD_TYPES = [
        {"name": "Truskawka", "color": (235, 45, 60), "size": 9},
        {"name": "Złoty Żołądź", "color": (245, 195, 40), "size": 11},
        {"name": "Jagoda", "color": (80, 110, 230), "size": 8},
        {"name": "Jabłko", "color": (220, 60, 40), "size": 10},
        {"name": "Borówka", "color": (120, 60, 180), "size": 8},
        {"name": "Grzyb Mocny", "color": (230, 130, 40), "size": 10},
    ]

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.type_info = random.choice(self.FOOD_TYPES)
        self.anim_offset = random.uniform(0, math.pi * 2)

    def draw(self, surface, cam_x, cam_y, anim_time):
        sx = int(self.x - cam_x + SCREEN_WIDTH // 2)
        sy = int(self.y - cam_y + SCREEN_HEIGHT // 2)

        # Rysowanie tylko widocznych na ekranie
        if -20 <= sx <= SCREEN_WIDTH + 20 and -20 <= sy <= SCREEN_HEIGHT + 20:
            bob = math.sin(anim_time * 5 + self.anim_offset) * 3
            cy = int(sy + bob)

            # Cień
            pygame.draw.ellipse(surface, (0, 0, 0, 60), (sx - 6, cy + 6, 12, 6))
            # Owoc
            pygame.draw.circle(surface, self.type_info["color"], (sx, cy), self.type_info["size"])
            pygame.draw.circle(surface, (255, 255, 255), (sx - 2, cy - 2), 2)


class ArenaNPC:
    """Zwierzę kibicujące graczowi na gigantycznej arenie."""

    def __init__(self, x, y, preset):
        self.x = float(x)
        self.y = float(y)
        self.preset = preset
        self.name = preset["name"]
        self.move_timer = random.uniform(1.0, 3.0)
        self.vx = 0.0
        self.vy = 0.0
        self.anim_time = random.uniform(0, 10)
        self.dialogues = [
            f"Kibicuję ci, {self.name} tutaj jest!",
            "Zbieraj owoce! Za każde dostaniesz +10 Mocy!",
            "Gigantyczna arena kryje ponad 300 smakołyków!",
            "Brama Lochu otworzy się na samej północy areny!",
            "Powodzenia w walce z Bossem!",
        ]
        self.current_dialogue = random.choice(self.dialogues)

    def update(self, dt):
        self.anim_time += dt
        self.move_timer -= dt

        if self.move_timer <= 0:
            self.move_timer = random.uniform(2.0, 5.0)
            if random.random() < 0.6:
                ang = random.uniform(0, math.pi * 2)
                sp = random.uniform(30, 60)
                self.vx = math.cos(ang) * sp
                self.vy = math.sin(ang) * sp
            else:
                self.vx = 0.0
                self.vy = 0.0

        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface, font, cam_x, cam_y, player_x, player_y):
        sx = self.x - cam_x + SCREEN_WIDTH // 2
        sy = self.y - cam_y + SCREEN_HEIGHT // 2

        if -60 <= sx <= SCREEN_WIDTH + 60 and -60 <= sy <= SCREEN_HEIGHT + 60:
            AnimalRenderer.render(
                surface,
                sx,
                sy,
                self.preset["id"],
                scale=1.0,
                anim_time=self.anim_time,
                is_moving=(self.vx != 0 or self.vy != 0),
            )

            dist = math.hypot(self.x - player_x, self.y - player_y)
            if dist < 110:
                txt_surf = font.render(self.current_dialogue, True, COLOR_TEXT)
                b_w = txt_surf.get_width() + 14
                b_h = txt_surf.get_height() + 8
                b_rect = pygame.Rect(sx - b_w // 2, sy - 58, b_w, b_h)

                pygame.draw.rect(surface, (25, 20, 16, 230), b_rect, border_radius=8)
                pygame.draw.rect(surface, COLOR_ACCENT, b_rect, width=1, border_radius=8)
                surface.blit(txt_surf, txt_surf.get_rect(center=b_rect.center))


class ArenaScene:
    """Gigantyczna Arena Jedzenia (100x większa, promien 3100 px, 300+ jedzenia, NPC, kamera)."""

    def __init__(self, player, sound_manager, on_enter_dungeon_cb, on_cancel_cb):
        self.player = player
        self.sound_manager = sound_manager
        self.on_enter_dungeon_cb = on_enter_dungeon_cb
        self.on_cancel_cb = on_cancel_cb

        self.font_timer = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_msg = pygame.font.SysFont("Arial", 22, bold=True)

        # Gigantyczna arena (promień 3100 px - 100x większa powierzchnia)
        self.center_x = 0.0
        self.center_y = 0.0
        self.radius = 3100.0

        # Stan czasowy
        self.timer_arena = ARENA_DURATION
        self.timer_rush = RUSH_DURATION
        self.phase = "EATING"

        # Brama Lochu na samej północy gigantycznej areny
        self.dungeon_gate_rect = pygame.Rect(-60, -int(self.radius) + 30, 120, 80)

        # Jedzenie (320 sztuk na raz)
        self.foods = []
        # NPC (16 duszki kibicujące)
        self.npcs = []

        self.float_texts = []
        self.anim_time = 0.0

    def start_challenge(self):
        self.timer_arena = ARENA_DURATION
        self.timer_rush = RUSH_DURATION
        self.phase = "EATING"
        self.player.reset_challenge()
        self.player.x = 0.0
        self.player.y = 0.0
        self.float_texts = []

        self._spawn_initial_foods(target_count=320)
        self._spawn_npcs(count=16)

    def _spawn_initial_foods(self, target_count=320):
        self.foods = []
        for _ in range(target_count):
            self._spawn_one_food()

    def _spawn_one_food(self):
        r = math.sqrt(random.random()) * (self.radius - 60)
        ang = random.uniform(0, math.pi * 2)
        fx = self.center_x + math.cos(ang) * r
        fy = self.center_y + math.sin(ang) * r
        self.foods.append(FoodItem(fx, fy))

    def _spawn_npcs(self, count=16):
        self.npcs = []
        presets = random.sample(ANIMAL_PRESETS, min(count, len(ANIMAL_PRESETS)))
        for p in presets:
            r = math.sqrt(random.random()) * (self.radius - 150)
            ang = random.uniform(0, math.pi * 2)
            nx = self.center_x + math.cos(ang) * r
            ny = self.center_y + math.sin(ang) * r
            self.npcs.append(ArenaNPC(nx, ny, p))

    def handle_event(self, event):
        pass

    def update(self, dt, keys):
        self.anim_time += dt

        # Ruch Gracza na gigantycznej arenie
        self.player.handle_input(keys, dt)

        # Ograniczenie kolizją do okręgu areny o promieniu 3100 px
        dist_from_center = math.hypot(self.player.x - self.center_x, self.player.y - self.center_y)
        if dist_from_center > self.radius - 25:
            ang = math.atan2(self.player.y - self.center_y, self.player.x - self.center_x)
            self.player.x = self.center_x + math.cos(ang) * (self.radius - 25)
            self.player.y = self.center_y + math.sin(ang) * (self.radius - 25)

        # NPC
        for npc in self.npcs:
            npc.update(dt)

        # Zbieranie jedzenia z 320+ owoców
        p_pos = (self.player.x, self.player.y)
        for food in self.foods[:]:
            if math.hypot(food.x - p_pos[0], food.y - p_pos[1]) < 32:
                self.foods.remove(food)
                self.player.power_points += 10
                self.sound_manager.play("eat")

                self.float_texts.append({
                    "text": "+10 MOCY!",
                    "x": food.x,
                    "y": food.y,
                    "life": 1.0,
                    "color": (255, 220, 60)
                })

                self._spawn_one_food()

        # Pływające teksty
        for ft in self.float_texts[:]:
            ft["y"] -= 25 * dt
            ft["life"] -= dt
            if ft["life"] <= 0:
                self.float_texts.remove(ft)

        # Zarządzanie czasem
        if self.phase == "EATING":
            self.timer_arena -= dt
            if self.timer_arena <= 0:
                self.timer_arena = 0.0
                self.phase = "RUSH"
                self.sound_manager.play("mirror")

        elif self.phase == "RUSH":
            self.timer_rush -= dt
            # Sprawdzenie czy gracz wszedł do wrót Lochu
            p_rect = self.player.rect.inflate(30, 30)
            if p_rect.colliderect(self.dungeon_gate_rect) or self.timer_rush <= 0:
                self.sound_manager.play("select")
                self.on_enter_dungeon_cb()

    def draw(self, surface):
        cam_x = self.player.x
        cam_y = self.player.y

        # Tło poza areną
        surface.fill((16, 12, 14))

        # Rysowanie gigantycznej okrągłej areny (przestrzeń świata)
        arena_sx = int(self.center_x - cam_x + SCREEN_WIDTH // 2)
        arena_sy = int(self.center_y - cam_y + SCREEN_HEIGHT // 2)

        pygame.draw.circle(surface, (60, 48, 38), (arena_sx, arena_sy), int(self.radius))
        pygame.draw.circle(surface, (80, 65, 50), (arena_sx, arena_sy), int(self.radius - 16))
        pygame.draw.circle(surface, (110, 90, 70), (arena_sx, arena_sy), int(self.radius), width=14)

        # Rysowanie 300+ jedzeń
        for food in self.foods:
            food.draw(surface, cam_x, cam_y, self.anim_time)

        # Brama Lochu na Północy Areny
        gate_sx = int(self.dungeon_gate_rect.x - cam_x + SCREEN_WIDTH // 2)
        gate_sy = int(self.dungeon_gate_rect.y - cam_y + SCREEN_HEIGHT // 2)
        gate_draw_rect = pygame.Rect(gate_sx, gate_sy, self.dungeon_gate_rect.width, self.dungeon_gate_rect.height)

        if -150 <= gate_sx <= SCREEN_WIDTH + 150 and -150 <= gate_sy <= SCREEN_HEIGHT + 150:
            gate_glow = int(180 + math.sin(self.anim_time * 8) * 70) if self.phase == "RUSH" else 100
            pygame.draw.rect(surface, (40, 25, 45), gate_draw_rect, border_radius=14)
            pygame.draw.rect(surface, (gate_glow, 40, 60), gate_draw_rect, width=4, border_radius=14)

            lbl_g = self.font_hud.render("LOCH", True, (255, 120, 140) if self.phase == "RUSH" else COLOR_TEXT_MUTED)
            surface.blit(lbl_g, (gate_draw_rect.centerx - lbl_g.get_width() // 2, gate_draw_rect.y + 24))

        # NPCs na arenie
        for npc in self.npcs:
            npc.draw(surface, self.font_hud, cam_x, cam_y, self.player.x, self.player.y)

        # Rysowanie Gracza
        self.player.draw(surface, camera_offset=(self.player.x - SCREEN_WIDTH // 2, self.player.y - SCREEN_HEIGHT // 2))

        # Pływające teksty "+10 MOCY!"
        for ft in self.float_texts:
            fsx = ft["x"] - cam_x + SCREEN_WIDTH // 2
            fsy = ft["y"] - cam_y + SCREEN_HEIGHT // 2
            txt_s = self.font_hud.render(ft["text"], True, ft["color"])
            surface.blit(txt_s, (fsx - txt_s.get_width() // 2, fsy))

        # --- HUD GÓRNY & KOMPAS ---
        hud_rect = pygame.Rect(SCREEN_WIDTH // 2 - 280, 15, 560, 68)
        pygame.draw.rect(surface, (25, 20, 16, 230), hud_rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_ACCENT, hud_rect, width=2, border_radius=12)

        if self.phase == "EATING":
            mins = int(self.timer_arena) // 60
            secs = int(self.timer_arena) % 60
            t_str = f"Czas Zbierania: {mins:02d}:{secs:02d}"
            t_col = (255, 230, 100)
        else:
            secs = int(max(0, self.timer_rush))
            t_str = f"WYŚCIG DO LOCHU! Pozostało: {secs:02d}s"
            t_col = (255, 80, 80)

        timer_surf = self.font_timer.render(t_str, True, t_col)
        surface.blit(timer_surf, (hud_rect.x + 20, hud_rect.y + 8))

        pow_surf = self.font_hud.render(f"PUNKTY MOCY: {self.player.power_points}", True, COLOR_SUCCESS)
        surface.blit(pow_surf, (hud_rect.x + 20, hud_rect.y + 42))

        # Kompas wskazujący Brama Lochu na Północy (0, -3050)
        gate_world_x = 0.0
        gate_world_y = -self.radius + 60
        ang_to_gate = math.atan2(gate_world_y - self.player.y, gate_world_x - self.player.x)

        comp_cx = hud_rect.right - 40
        comp_cy = hud_rect.centery
        pygame.draw.circle(surface, (40, 30, 25), (comp_cx, comp_cy), 20)
        pygame.draw.circle(surface, (255, 120, 140) if self.phase == "RUSH" else COLOR_ACCENT, (comp_cx, comp_cy), 20, width=2)
        arrow_ex = comp_cx + math.cos(ang_to_gate) * 14
        arrow_ey = comp_cy + math.sin(ang_to_gate) * 14
        pygame.draw.line(surface, (255, 60, 80), (comp_cx, comp_cy), (arrow_ex, arrow_ey), 4)

        # Opis pod kompasem
        c_lbl = self.font.render("Loch", True, COLOR_TEXT_MUTED)
        surface.blit(c_lbl, (comp_cx - c_lbl.get_width() // 2, comp_cy + 22))

        # Komunikat RUSH
        if self.phase == "RUSH":
            msg_surf = self.font_msg.render("CZAS MINĄŁ! BIEGNIJ DO WROT LOCHU NA PÓŁNOCY (PODĄŻAJ ZA STRZAŁKĄ KOMPASU)!", True, (255, 60, 70))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 105))
            pygame.draw.rect(surface, (35, 10, 15, 240), msg_rect.inflate(30, 14), border_radius=8)
            surface.blit(msg_surf, msg_rect)
