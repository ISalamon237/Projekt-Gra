import pygame
import math
import random
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT,
    COLOR_ACCENT,
    COLOR_TEXT_MUTED,
)


class NestScene:
    """Scena przytulnego Gniazda Gracza z interakcjami i ciepłym oświetleniem."""

    def __init__(self, player, sound_manager, on_open_mirror_cb, on_exit_to_forest_cb, on_start_play_cb=None):
        self.player = player
        self.sound_manager = sound_manager
        self.on_open_mirror_cb = on_open_mirror_cb
        self.on_exit_to_forest_cb = on_exit_to_forest_cb
        self.on_start_play_cb = on_start_play_cb

        self.font_ui = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 22, bold=True)

        # Granice gniazda i ściany (kolizje)
        self.walls = [
            pygame.Rect(0, 0, SCREEN_WIDTH, 120),          # Górna ściana
            pygame.Rect(0, 0, 100, SCREEN_HEIGHT),          # Lewa ściana
            pygame.Rect(SCREEN_WIDTH - 100, 0, 100, SCREEN_HEIGHT), # Prawa ściana
            pygame.Rect(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60),  # Dolna ściana
        ]

        # Obiekty interaktywne w gnieździe
        self.play_altar_rect = pygame.Rect(180, SCREEN_HEIGHT - 170, 90, 70)  # Ołtarz Graj
        self.mirror_rect = pygame.Rect(180, 140, 70, 90)
        self.bed_rect = pygame.Rect(SCREEN_WIDTH - 260, 150, 120, 90)
        self.snack_rect = pygame.Rect(340, SCREEN_HEIGHT - 160, 80, 60)
        self.door_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 100, 100, 40)
        self.fireplace_rect = pygame.Rect(SCREEN_WIDTH // 2 - 40, 130, 80, 70)

        # Dodatkowe kolizje z meblami
        self.walls.extend([
            self.fireplace_rect,
            pygame.Rect(self.mirror_rect.x, self.mirror_rect.y + 40, self.mirror_rect.width, 30),
            pygame.Rect(self.bed_rect.x, self.bed_rect.y + 20, self.bed_rect.width, 50),
            self.play_altar_rect,
        ])


        # Efekty cząsteczkowe kominka i snu
        self.particles = []
        self.sleep_particles = []
        self.anim_time = 0.0
        self.interaction_msg = ""
        self.interaction_timer = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e or event.key == pygame.K_SPACE:
                self._check_interactions()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            p_rect = self.player.rect.inflate(60, 60)
            if self.play_altar_rect.collidepoint(m_pos) and p_rect.colliderect(self.play_altar_rect):
                if self.on_start_play_cb:
                    self.sound_manager.play("mirror")
                    self.on_start_play_cb()
            elif self.mirror_rect.collidepoint(m_pos) and p_rect.colliderect(self.mirror_rect):
                self.sound_manager.play("mirror")
                self.on_open_mirror_cb()
            elif self.bed_rect.collidepoint(m_pos) and p_rect.colliderect(self.bed_rect):
                self._sleep()
            elif self.snack_rect.collidepoint(m_pos) and p_rect.colliderect(self.snack_rect):
                self._eat_snack()
            elif self.door_rect.collidepoint(m_pos) and p_rect.colliderect(self.door_rect):
                self.sound_manager.play("step")
                self.on_exit_to_forest_cb()

    def _check_interactions(self):
        p_rect = self.player.rect.inflate(50, 50)
        if p_rect.colliderect(self.play_altar_rect) and self.on_start_play_cb:
            self.sound_manager.play("mirror")
            self.on_start_play_cb()
        elif p_rect.colliderect(self.mirror_rect):
            self.sound_manager.play("mirror")
            self.on_open_mirror_cb()
        elif p_rect.colliderect(self.bed_rect):
            self._sleep()
        elif p_rect.colliderect(self.snack_rect):
            self._eat_snack()
        elif p_rect.colliderect(self.door_rect):
            self.sound_manager.play("step")
            self.on_exit_to_forest_cb()


    def _sleep(self):
        self.sound_manager.play("sleep")
        self.interaction_msg = "Odpoczęto w miękkim posłaniu gniazda! ZZZ..."
        self.interaction_timer = 3.0
        for _ in range(8):
            self.sleep_particles.append({
                "x": self.player.x + random.randint(-20, 20),
                "y": self.player.y - 40,
                "vy": - random.uniform(15, 30),
                "life": 1.5,
                "size": random.randint(14, 20)
            })

    def _eat_snack(self):
        self.sound_manager.play("eat")
        self.player.speed_boost_timer = 6.0
        self.interaction_msg = "Zjedzono soczystą leśną jagodę! Prędkość ruchu wzrosła!"
        self.interaction_timer = 3.0

    def update(self, dt, keys):
        self.anim_time += dt
        self.player.handle_input(keys, dt, obstacles=self.walls)

        if self.interaction_timer > 0:
            self.interaction_timer -= dt

        # Cząsteczki iskier kominka
        if random.random() < 0.4:
            self.particles.append({
                "x": self.fireplace_rect.centerx + random.randint(-15, 15),
                "y": self.fireplace_rect.centery - 10,
                "vx": random.uniform(-10, 10),
                "vy": -random.uniform(20, 50),
                "life": random.uniform(0.6, 1.2),
                "color": random.choice([(255, 180, 40), (255, 100, 30), (240, 220, 80)])
            })

        for p in self.particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        for sp in self.sleep_particles[:]:
            sp["y"] += sp["vy"] * dt
            sp["life"] -= dt
            if sp["life"] <= 0:
                self.sleep_particles.remove(sp)

    def draw(self, surface):
        # Tło drewnianego gniazda
        surface.fill((45, 33, 24))

        # Rysowanie podłogi z plecionki/liści
        floor_rect = pygame.Rect(100, 120, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 180)
        pygame.draw.rect(surface, (62, 46, 34), floor_rect, border_radius=30)
        pygame.draw.rect(surface, (84, 62, 45), floor_rect, width=6, border_radius=30)

        # Dywan z mchu
        pygame.draw.ellipse(surface, (55, 95, 45), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80, 300, 160))

        # 0. Ołtarz "GRAJ" / Portal Wyzwania
        pa = self.play_altar_rect
        pygame.draw.rect(surface, (70, 45, 85), pa, border_radius=12)
        glow_c = int(200 + math.sin(self.anim_time * 6) * 45)
        pygame.draw.rect(surface, (glow_c, 160, 50), pa, width=3, border_radius=12)

        lbl_play = self.font_title.render("GRAJ!", True, (255, 220, 80))
        surface.blit(lbl_play, (pa.centerx - lbl_play.get_width() // 2, pa.centery - 12))
        lbl_p_sub = self.font_ui.render("Ołtarz Wyzwania", True, COLOR_TEXT)
        surface.blit(lbl_p_sub, (pa.centerx - lbl_p_sub.get_width() // 2, pa.y - 20))

        # 1. Kominek

        fp = self.fireplace_rect
        pygame.draw.rect(surface, (70, 70, 75), fp, border_radius=10)
        pygame.draw.rect(surface, (40, 40, 45), fp.inflate(-10, -10), border_radius=8)
        # Ogień
        flame_h = int(18 + math.sin(self.anim_time * 12) * 4)
        flame_rect = pygame.Rect(fp.centerx - 12, fp.bottom - 24 - flame_h, 24, flame_h)
        pygame.draw.ellipse(surface, (245, 120, 30), flame_rect)
        pygame.draw.ellipse(surface, (255, 220, 60), flame_rect.inflate(-8, -6))

        # Iskry kominka
        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), int(3 * p["life"]))

        # 2. Magiczne Lustro (Personalizacja)
        mr = self.mirror_rect
        pygame.draw.rect(surface, (120, 90, 50), mr, border_radius=15)
        mirror_glass = mr.inflate(-12, -14)
        glass_glow = int(180 + math.sin(self.anim_time * 3) * 40)
        pygame.draw.rect(surface, (100, 160, 220), mirror_glass, border_radius=10)
        pygame.draw.rect(surface, (glass_glow, glass_glow, 255), mirror_glass, width=2, border_radius=10)
        # Napis na lustrze
        lbl_m = self.font_ui.render("Lustro", True, COLOR_TEXT)
        surface.blit(lbl_m, (mr.centerx - lbl_m.get_width() // 2, mr.y - 20))

        # 3. Posłanie z liści i poduszek
        br = self.bed_rect
        pygame.draw.rect(surface, (135, 95, 55), br, border_radius=12)
        pygame.draw.rect(surface, (225, 210, 180), br.inflate(-12, -12), border_radius=8)
        pygame.draw.ellipse(surface, (220, 90, 100), (br.x + 10, br.y + 10, 40, 26))

        lbl_b = self.font_ui.render("Posłanie", True, COLOR_TEXT)
        surface.blit(lbl_b, (br.centerx - lbl_b.get_width() // 2, br.y - 20))

        # 4. Misa z przekąskami
        sr = self.snack_rect
        pygame.draw.ellipse(surface, (110, 75, 45), sr)
        pygame.draw.circle(surface, (210, 40, 60), (sr.centerx - 10, sr.centery - 4), 7)
        pygame.draw.circle(surface, (220, 50, 70), (sr.centerx + 8, sr.centery - 2), 8)
        pygame.draw.circle(surface, (180, 30, 50), (sr.centerx, sr.centery + 6), 6)

        lbl_s = self.font_ui.render("Przekąski", True, COLOR_TEXT)
        surface.blit(lbl_s, (sr.centerx - lbl_s.get_width() // 2, sr.y - 20))

        # 5. Wyjście do Lasu
        dr = self.door_rect
        pygame.draw.rect(surface, (30, 80, 40), dr, border_radius=8)
        pygame.draw.rect(surface, (100, 200, 90), dr, width=2, border_radius=8)
        lbl_d = self.font_ui.render("Wyjście na Polanę [Las]", True, (230, 255, 220))
        surface.blit(lbl_d, (dr.centerx - lbl_d.get_width() // 2, dr.y + 10))

        # Rysowanie Gracza
        self.player.draw(surface)

        # Cząsteczki snu
        for sp in self.sleep_particles:
            z_surf = self.font_title.render("Z", True, (160, 220, 255))
            surface.blit(z_surf, (sp["x"], sp["y"]))

        # Podpowiedź interakcji na dole
        p_rect = self.player.rect.inflate(50, 50)
        hint = ""
        if p_rect.colliderect(self.play_altar_rect):
            hint = "Naciśnij [E] lub Kliknij Ołtarz, aby GRAĆ (Arena Jedzenia -> Loch -> Walka z Bossem)"
        elif p_rect.colliderect(self.mirror_rect):
            hint = "Naciśnij [E] lub Kliknij Lustro, aby zmienić wygląd / nazwę postaci"
        elif p_rect.colliderect(self.bed_rect):
            hint = "Naciśnij [E] lub Kliknij Posłanie, aby odpocząć"
        elif p_rect.colliderect(self.snack_rect):
            hint = "Naciśnij [E] lub Kliknij Przekąski, aby zjeść leśną jagodę"
        elif p_rect.colliderect(self.door_rect):
            hint = "Naciśnij [E] lub Kliknij Wyjście, aby wyjść z Gniazda do Lasu"


        if hint:
            h_surf = self.font_ui.render(hint, True, COLOR_ACCENT)
            h_rect = h_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            bg_h = h_rect.inflate(20, 10)
            pygame.draw.rect(surface, (20, 16, 12, 220), bg_h, border_radius=6)
            pygame.draw.rect(surface, COLOR_ACCENT, bg_h, width=1, border_radius=6)
            surface.blit(h_surf, h_rect)

        # Wiadomość o zdarzeniu (np. zjedzenie przekąski)
        if self.interaction_timer > 0 and self.interaction_msg:
            m_surf = self.font_ui.render(self.interaction_msg, True, (255, 240, 180))
            m_rect = m_surf.get_rect(center=(SCREEN_WIDTH // 2, 75))
            pygame.draw.rect(surface, (30, 24, 18, 230), m_rect.inflate(24, 12), border_radius=8)
            surface.blit(m_surf, m_rect)
