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
from animal_presets import ANIMAL_PRESETS
from animal_renderer import AnimalRenderer
from ui import Button


CHUNK_SIZE = 800

# Typy Leśnych Jagód
BERRY_TYPES = [
    {
        "type": "GOLDEN",
        "name": "Złota Jagoda",
        "color": (255, 215, 40),
        "effect_type": "REWARD",
        "power_change": 50,
        "msg": "+50 MOCY! (Złota Jagoda)",
    },
    {
        "type": "SPEED",
        "name": "Błyskawiczna Jagoda",
        "color": (80, 220, 255),
        "effect_type": "REWARD",
        "power_change": 20,
        "msg": "SUPER PRĘDKOŚĆ RUCHU! (+20 Mocy)",
    },
    {
        "type": "HEAL",
        "name": "Lecznicza Jagoda",
        "color": (245, 100, 150),
        "effect_type": "REWARD",
        "power_change": 15,
        "msg": "ODNOWIONO ZDROWIE! (+15 Mocy)",
    },
    {
        "type": "POISON",
        "name": "Trująca Jagoda",
        "color": (160, 40, 200),
        "effect_type": "PENALTY",
        "power_change": -15,
        "msg": "-15 MOCY! TRUCIZNA (Spowolnienie)",
    },
    {
        "type": "GHOST",
        "name": "Mroczna Jagoda",
        "color": (70, 30, 90),
        "effect_type": "PENALTY",
        "power_change": -10,
        "msg": "OSZOŁOMIENIE! (Zamrożenie)",
    },
    {
        "type": "THORN",
        "name": "Kłująca Jagoda",
        "color": (200, 60, 40),
        "effect_type": "PENALTY",
        "power_change": -5,
        "msg": "CIERNIE! Odrzucenie!",
    },
]


class Bush:
    """Proceduralny krzak leśny z ukrytą jagodą."""

    def __init__(self, x, y, berry_info):
        self.x = float(x)
        self.y = float(y)
        self.radius = 28
        self.has_berry = True
        self.berry_info = berry_info

    def draw(self, surface, cam_x, cam_y, anim_time):
        screen_x = int(self.x - cam_x + SCREEN_WIDTH // 2)
        screen_y = int(self.y - cam_y + SCREEN_HEIGHT // 2)

        # Optymalizacja: rysuj tylko widoczne na ekranie
        if -50 <= screen_x <= SCREEN_WIDTH + 50 and -50 <= screen_y <= SCREEN_HEIGHT + 50:
            # Cień pod krzakiem
            pygame.draw.ellipse(surface, (0, 0, 0, 70), (screen_x - 30, screen_y + 12, 60, 20))

            # Korona krzaka
            pygame.draw.circle(surface, (30, 85, 40), (screen_x - 12, screen_y - 8), 18)
            pygame.draw.circle(surface, (40, 105, 50), (screen_x + 12, screen_y - 8), 18)
            pygame.draw.circle(surface, (50, 125, 60), (screen_x, screen_y - 18), 20)
            pygame.draw.circle(surface, (35, 95, 45), (screen_x, screen_y), 22)

            # Widoczna jagoda
            if self.has_berry:
                b_color = self.berry_info["color"]
                bob = math.sin(anim_time * 4 + self.x) * 2
                pygame.draw.circle(surface, b_color, (screen_x - 6, int(screen_y - 6 + bob)), 6)
                pygame.draw.circle(surface, b_color, (screen_x + 8, int(screen_y + 2 + bob)), 5)
                pygame.draw.circle(surface, (255, 255, 255), (screen_x - 7, int(screen_y - 7 + bob)), 2)


class NPC:
    """Postać niezależna wędrująca po chunkach lasu."""

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
            f"Cześć! Jestem {self.name}!",
            "Ten las jest naprawdę nieskończenie długi!",
            "Im głębiej wejdziesz w las, tym więcej złotych jagód!",
            "Sprawdzaj kompas w HUD aby wrócić do gniazda.",
            "Uważaj na trujące fioletowe jagody!",
        ]
        self.current_dialogue = random.choice(self.dialogues)

    def update(self, dt):
        self.anim_time += dt
        self.move_timer -= dt

        if self.move_timer <= 0:
            self.move_timer = random.uniform(2.0, 5.0)
            if random.random() < 0.6:
                ang = random.uniform(0, math.pi * 2)
                sp = random.uniform(20, 50)
                self.vx = math.cos(ang) * sp
                self.vy = math.sin(ang) * sp
            else:
                self.vx = 0.0
                self.vy = 0.0

        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface, font, cam_x, cam_y, player_x, player_y):
        screen_x = self.x - cam_x + SCREEN_WIDTH // 2
        screen_y = self.y - cam_y + SCREEN_HEIGHT // 2

        if -60 <= screen_x <= SCREEN_WIDTH + 60 and -60 <= screen_y <= SCREEN_HEIGHT + 60:
            AnimalRenderer.render(
                surface,
                screen_x,
                screen_y,
                self.preset["id"],
                scale=1.0,
                anim_time=self.anim_time,
                is_moving=(self.vx != 0 or self.vy != 0),
            )

            dist = math.hypot(self.x - player_x, self.y - player_y)
            if dist < 100:
                txt_surf = font.render(self.current_dialogue, True, COLOR_TEXT)
                b_w = txt_surf.get_width() + 14
                b_h = txt_surf.get_height() + 8
                b_rect = pygame.Rect(screen_x - b_w // 2, screen_y - 58, b_w, b_h)

                pygame.draw.rect(surface, (25, 20, 16, 230), b_rect, border_radius=8)
                pygame.draw.rect(surface, COLOR_ACCENT, b_rect, width=1, border_radius=8)
                surface.blit(txt_surf, txt_surf.get_rect(center=b_rect.center))


class ForestChunk:
    """Proceduralny sektor nieskończonego lasu."""

    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.origin_x = cx * CHUNK_SIZE
        self.origin_y = cy * CHUNK_SIZE

        # Pseudo-losowe generowanie zawartości chunkera
        seed = (cx * 73856093) ^ (cy * 19349663)
        rng = random.Random(seed)

        self.trees = []
        self.bushes = []
        self.npcs = []
        self.flowers = []

        # Drzewa
        tree_count = rng.randint(5, 10)
        for _ in range(tree_count):
            tx = self.origin_x + rng.randint(40, CHUNK_SIZE - 40)
            ty = self.origin_y + rng.randint(40, CHUNK_SIZE - 40)
            self.trees.append((tx, ty, rng.randint(30, 46)))

        # Krzaki z jagodami
        bush_count = rng.randint(5, 9)
        weights = [0.20, 0.25, 0.25, 0.12, 0.10, 0.08]
        for _ in range(bush_count):
            bx = self.origin_x + rng.randint(40, CHUNK_SIZE - 40)
            by = self.origin_y + rng.randint(40, CHUNK_SIZE - 40)
            b_info = rng.choices(BERRY_TYPES, weights=weights)[0]
            self.bushes.append(Bush(bx, by, b_info))

        # Kwiaty
        flower_count = rng.randint(8, 15)
        for _ in range(flower_count):
            fx = self.origin_x + rng.randint(20, CHUNK_SIZE - 20)
            fy = self.origin_y + rng.randint(20, CHUNK_SIZE - 20)
            self.flowers.append((fx, fy, rng.choice([(245, 230, 90), (240, 110, 160), (120, 200, 255)])))

        # NPC
        if rng.random() < 0.6 and not (cx == 0 and cy == 0):
            nx = self.origin_x + rng.randint(100, CHUNK_SIZE - 100)
            ny = self.origin_y + rng.randint(100, CHUNK_SIZE - 100)
            preset = rng.choice(ANIMAL_PRESETS)
            self.npcs.append(NPC(nx, ny, preset))


class ForestScene:
    """Prawdziwy Nieskończony Las (Infinite Forest) z systemem Kamery i Chunków."""

    def __init__(self, player, sound_manager, on_return_to_nest_cb):
        self.player = player
        self.sound_manager = sound_manager
        self.on_return_to_nest_cb = on_return_to_nest_cb

        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 22, bold=True)

        self.btn_nest = Button(
            (40, 25, 200, 40),
            "<- Powrót do Gniazda",
            callback=self._teleport_to_nest,
            color=(45, 65, 35),
            hover_color=(65, 95, 50),
            font_size=16,
        )

        self.chunks = {}
        self.float_texts = []
        self.status_msg = ""
        self.status_timer = 0.0
        self.slow_timer = 0.0
        self.speed_boost_timer = 0.0

        self.anim_time = 0.0

    def enter_forest(self):
        # Wejście do lasu tuż obok portalu gniazda (0, 0)
        self.player.x = 0
        self.player.y = 120

    def _teleport_to_nest(self):
        self.sound_manager.play("step")
        if self.on_return_to_nest_cb:
            self.on_return_to_nest_cb()

    def _get_or_create_chunk(self, cx, cy):
        key = (cx, cy)
        if key not in self.chunks:
            self.chunks[key] = ForestChunk(cx, cy)
        return self.chunks[key]

    def handle_event(self, event):
        self.btn_nest.handle_event(event)

        if event.type == pygame.KEYDOWN and (event.key == pygame.K_e or event.key == pygame.K_SPACE):
            self._search_nearby_bush()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._search_nearby_bush(click_pos=event.pos)

    def _search_nearby_bush(self, click_pos=None):
        p_x, p_y = self.player.x, self.player.y
        current_cx = int(p_x // CHUNK_SIZE)
        current_cy = int(p_y // CHUNK_SIZE)

        # Przeszukanie krzaków w sąsiednich chunkach
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                chunk = self._get_or_create_chunk(current_cx + dx, current_cy + dy)
                for bush in chunk.bushes:
                    if bush.has_berry:
                        dist = math.hypot(bush.x - p_x, bush.y - p_y)

                        is_clicked = False
                        if click_pos:
                            screen_bx = bush.x - p_x + SCREEN_WIDTH // 2
                            screen_by = bush.y - p_y + SCREEN_HEIGHT // 2
                            is_clicked = math.hypot(click_pos[0] - screen_bx, click_pos[1] - screen_by) < 30

                        if dist < 65 or is_clicked:
                            bush.has_berry = False
                            info = bush.berry_info

                            self.player.power_points = max(0, self.player.power_points + info["power_change"])
                            self.status_msg = info["msg"]
                            self.status_timer = 3.5

                            if info["type"] == "GOLDEN":
                                self.sound_manager.play("mirror")
                            elif info["type"] == "SPEED":
                                self.sound_manager.play("eat")
                                self.speed_boost_timer = 12.0
                            elif info["type"] == "HEAL":
                                self.sound_manager.play("sleep")
                                self.player.hp = self.player.max_hp
                            elif info["type"] == "POISON":
                                self.sound_manager.play("step")
                                self.slow_timer = 6.0
                            elif info["type"] == "THORN":
                                self.sound_manager.play("click")
                                self.player.x += random.choice([-50, 50])
                                self.player.y += random.choice([-50, 50])

                            col = COLOR_SUCCESS if info["effect_type"] == "REWARD" else (240, 60, 70)
                            self.float_texts.append({
                                "text": info["msg"],
                                "x": bush.x,
                                "y": bush.y - 15,
                                "life": 1.4,
                                "color": col
                            })
                            return

    def update(self, dt, keys):
        self.anim_time += dt

        if self.status_timer > 0:
            self.status_timer -= dt
        if self.slow_timer > 0:
            self.slow_timer -= dt
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt

        orig_speed = self.player.speed
        if self.speed_boost_timer > 0:
            self.player.speed = orig_speed * 1.6
        elif self.slow_timer > 0:
            self.player.speed = orig_speed * 0.4
        else:
            self.player.speed = orig_speed

        # Ruch Gracza BEZ ŻADNYCH OGRANICZEŃ (Prawdziwy Nieskończony Las!)
        self.player.handle_input(keys, dt)
        self.player.speed = orig_speed

        # Aktualizacja NPC w ładowanych chunkach
        p_cx = int(self.player.x // CHUNK_SIZE)
        p_cy = int(self.player.y // CHUNK_SIZE)

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                chunk = self._get_or_create_chunk(p_cx + dx, p_cy + dy)
                for npc in chunk.npcs:
                    npc.update(dt)

        # Pływające teksty
        for ft in self.float_texts[:]:
            ft["y"] -= 20 * dt
            ft["life"] -= dt
            if ft["life"] <= 0:
                self.float_texts.remove(ft)

    def draw(self, surface):
        cam_x = self.player.x
        cam_y = self.player.y

        # Tło trawy w nieskończonym lesie
        surface.fill((42, 88, 48))

        # Ładowanie i rysowanie sąsiednich chunków
        p_cx = int(self.player.x // CHUNK_SIZE)
        p_cy = int(self.player.y // CHUNK_SIZE)

        # Portal powrotny do gniazda na współrzędnych (0, 0)
        portal_sx = 0 - cam_x + SCREEN_WIDTH // 2
        portal_sy = 0 - cam_y + SCREEN_HEIGHT // 2
        if -100 <= portal_sx <= SCREEN_WIDTH + 100 and -100 <= portal_sy <= SCREEN_HEIGHT + 100:
            pygame.draw.circle(surface, (80, 50, 30), (int(portal_sx), int(portal_sy)), 40)
            pygame.draw.circle(surface, (100, 200, 90), (int(portal_sx), int(portal_sy)), 40, width=3)
            lbl_p = self.font.render("Portal do Gniazda (0,0)", True, (240, 255, 220))
            surface.blit(lbl_p, (portal_sx - lbl_p.get_width() // 2, portal_sy - 55))

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                chunk = self._get_or_create_chunk(p_cx + dx, p_cy + dy)

                # Kwiaty
                for fx, fy, fcol in chunk.flowers:
                    fsx = int(fx - cam_x + SCREEN_WIDTH // 2)
                    fsy = int(fy - cam_y + SCREEN_HEIGHT // 2)
                    if 0 <= fsx <= SCREEN_WIDTH and 0 <= fsy <= SCREEN_HEIGHT:
                        pygame.draw.circle(surface, fcol, (fsx, fsy), 4)

                # Krzaki
                for bush in chunk.bushes:
                    bush.draw(surface, cam_x, cam_y, self.anim_time)

                # NPCs
                for npc in chunk.npcs:
                    npc.draw(surface, self.font, cam_x, cam_y, self.player.x, self.player.y)

                # Drzewa
                for tx, ty, tr in chunk.trees:
                    tsx = int(tx - cam_x + SCREEN_WIDTH // 2)
                    tsy = int(ty - cam_y + SCREEN_HEIGHT // 2)
                    if -60 <= tsx <= SCREEN_WIDTH + 60 and -60 <= tsy <= SCREEN_HEIGHT + 60:
                        pygame.draw.rect(surface, (60, 42, 25), (tsx - 8, tsy - 5, 16, 25))
                        pygame.draw.circle(surface, (30, 70, 38), (tsx, tsy - 20), tr)
                        pygame.draw.circle(surface, (45, 95, 50), (tsx - 8, tsy - 25), tr - 8)

        # Rysowanie Gracza (na środku ekranu podążającego za nim)
        self.player.draw(surface, camera_offset=(self.player.x - SCREEN_WIDTH // 2, self.player.y - SCREEN_HEIGHT // 2))

        # Pływające teksty nagród/kar
        for ft in self.float_texts:
            fsx = ft["x"] - cam_x + SCREEN_WIDTH // 2
            fsy = ft["y"] - cam_y + SCREEN_HEIGHT // 2
            t_s = self.font_hud.render(ft["text"], True, ft["color"])
            bg_t = t_s.get_rect(center=(fsx, fsy)).inflate(12, 6)
            pygame.draw.rect(surface, (20, 16, 12, 200), bg_t, border_radius=6)
            surface.blit(t_s, t_s.get_rect(center=(fsx, fsy)))

        self.btn_nest.draw(surface)

        # --- HUD NIESKOŃCZONEGO LASU ---
        hud_r = pygame.Rect(SCREEN_WIDTH - 380, 20, 340, 60)
        pygame.draw.rect(surface, (25, 20, 16, 230), hud_r, border_radius=10)
        pygame.draw.rect(surface, COLOR_ACCENT, hud_r, width=2, border_radius=10)

        # Licznik głębokości lasu w metrach od gniazda (0,0)
        dist_m = int(math.hypot(self.player.x, self.player.y) / 10)
        dist_s = self.font_hud.render(f"Głębokość Lasu: {dist_m} m", True, (255, 220, 100))
        surface.blit(dist_s, (hud_r.x + 14, hud_r.y + 8))

        pow_s = self.font_hud.render(f"PUNKTY MOCY: {self.player.power_points}", True, COLOR_SUCCESS)
        surface.blit(pow_s, (hud_r.x + 14, hud_r.y + 32))

        # Kompas wskazujący portal (0,0)
        ang_to_nest = math.atan2(0 - self.player.y, 0 - self.player.x)
        comp_cx = hud_r.right - 35
        comp_cy = hud_r.centery
        pygame.draw.circle(surface, (40, 30, 25), (comp_cx, comp_cy), 18)
        pygame.draw.circle(surface, COLOR_ACCENT, (comp_cx, comp_cy), 18, width=2)
        arrow_ex = comp_cx + math.cos(ang_to_nest) * 12
        arrow_ey = comp_cy + math.sin(ang_to_nest) * 12
        pygame.draw.line(surface, (255, 80, 80), (comp_cx, comp_cy), (arrow_ex, arrow_ey), 3)

        # Baner informacyjny
        if self.status_timer > 0 and self.status_msg:
            st_s = self.font_hud.render(self.status_msg, True, (255, 240, 180))
            st_r = st_s.get_rect(center=(SCREEN_WIDTH // 2, 75))
            pygame.draw.rect(surface, (30, 24, 18, 230), st_r.inflate(24, 12), border_radius=8)
            surface.blit(st_s, st_r)
