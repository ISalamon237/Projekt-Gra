import pygame
import math
from animal_presets import ANIMAL_BY_ID


class AnimalRenderer:
    """Proceduralny silnik rysujący postaci 50 zwierząt w Pygame z użyciem grafiki wektorowej."""

    @staticmethod
    def render(
        surface,
        x,
        y,
        animal_id,
        color_body=None,
        color_accent=None,
        color_eye=None,
        accessory="Brak",
        scale=1.0,
        anim_time=0.0,
        is_moving=False,
        direction="down",
    ):
        preset = ANIMAL_BY_ID.get(animal_id, ANIMAL_BY_ID["fox"])

        c_body = color_body or preset["color_body"]
        c_accent = color_accent or preset["color_accent"]
        c_eye = color_eye or preset["color_eye"]

        # Obliczenie bobbing / animacji
        bob = math.sin(anim_time * 6) * (3 * scale) if is_moving else math.sin(anim_time * 2) * (1.5 * scale)
        leg_angle = math.sin(anim_time * 10) * 0.4 if is_moving else 0.0
        blink = (math.sin(anim_time * 0.8) > 0.95)

        # Cień pod postacią
        shadow_rect = pygame.Rect(0, 0, int(36 * scale), int(12 * scale))
        shadow_rect.center = (int(x), int(y + 24 * scale))
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 90), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_rect.topleft)

        center_x = x
        center_y = y + bob

        # Rysowanie skrzydeł (z tyłu)
        specials = preset["special"]
        if "wings" in specials or "bat_wings" in specials or "glossy_wings" in specials or "fast_wings" in specials:
            wing_flap = math.sin(anim_time * 8) * 0.2 if is_moving else math.sin(anim_time * 3) * 0.1
            wing_color = c_accent if "bat_wings" not in specials else (50, 40, 60)
            # Lewe skrzydło
            w1 = [(center_x - 12 * scale, center_y - 4 * scale),
                  (center_x - (36 + wing_flap * 10) * scale, center_y - (20 + wing_flap * 15) * scale),
                  (center_x - 24 * scale, center_y + 10 * scale)]
            # Prawe skrzydło
            w2 = [(center_x + 12 * scale, center_y - 4 * scale),
                  (center_x + (36 + wing_flap * 10) * scale, center_y - (20 + wing_flap * 15) * scale),
                  (center_x + 24 * scale, center_y + 10 * scale)]
            pygame.draw.polygon(surface, wing_color, w1)
            pygame.draw.polygon(surface, (max(0, wing_color[0]-30), max(0, wing_color[1]-30), max(0, wing_color[2]-30)), w1, int(2 * scale))
            pygame.draw.polygon(surface, wing_color, w2)
            pygame.draw.polygon(surface, (max(0, wing_color[0]-30), max(0, wing_color[1]-30), max(0, wing_color[2]-30)), w2, int(2 * scale))

        # Rysowanie ogona
        tail_type = preset["tail_type"]
        tail_wag = math.sin(anim_time * 6) * 0.3 if is_moving else math.sin(anim_time * 2.5) * 0.15
        if tail_type == "bushy":
            tx = center_x + math.sin(tail_wag) * 20 * scale + (18 * scale)
            ty = center_y + 4 * scale
            pygame.draw.circle(surface, c_body, (int(tx), int(ty)), int(14 * scale))
            if "tail_tip_white" in specials:
                pygame.draw.circle(surface, c_accent, (int(tx + 4 * scale), int(ty - 4 * scale)), int(7 * scale))
        elif tail_type == "fluffy_ball":
            pygame.draw.circle(surface, c_accent, (int(center_x + 18 * scale), int(center_y + 10 * scale)), int(8 * scale))
        elif tail_type == "long_thin":
            t_pts = [(center_x + 10 * scale, center_y + 10 * scale),
                     (center_x + (22 + tail_wag * 10) * scale, center_y + 16 * scale),
                     (center_x + (28 + tail_wag * 15) * scale, center_y + 6 * scale)]
            pygame.draw.lines(surface, c_body, False, t_pts, int(5 * scale))
        elif tail_type == "dragon_tail":
            t_pts = [(center_x + 10 * scale, center_y + 10 * scale),
                     (center_x + (24 + tail_wag * 12) * scale, center_y + 14 * scale),
                     (center_x + (32 + tail_wag * 16) * scale, center_y + 4 * scale)]
            pygame.draw.lines(surface, c_body, False, t_pts, int(6 * scale))
            # Grot ogona
            pygame.draw.polygon(surface, c_accent, [
                (t_pts[-1][0], t_pts[-1][1] - 6 * scale),
                (t_pts[-1][0] + 8 * scale, t_pts[-1][1]),
                (t_pts[-1][0], t_pts[-1][1] + 6 * scale)
            ])
        elif tail_type == "feather_fan":
            pygame.draw.polygon(surface, c_accent, [
                (center_x, center_y + 10 * scale),
                (center_x - 16 * scale, center_y + 28 * scale),
                (center_x + 16 * scale, center_y + 28 * scale)
            ])

        # Rysowanie nóg / łapek
        leg_offset = math.sin(anim_time * 12) * 6 * scale if is_moving else 0
        l_color = (max(0, c_body[0]-40), max(0, c_body[1]-40), max(0, c_body[2]-40))
        pygame.draw.circle(surface, l_color, (int(center_x - 10 * scale), int(center_y + 18 * scale + leg_offset)), int(5 * scale))
        pygame.draw.circle(surface, l_color, (int(center_x + 10 * scale), int(center_y + 18 * scale - leg_offset)), int(5 * scale))

        # Kształt Tułowia i Głowy
        b_shape = preset["body_shape"]
        head_radius = int(20 * scale)
        body_radius = int(22 * scale)

        if b_shape == "bear":
            body_radius = int(25 * scale)
        elif b_shape == "slender":
            body_radius = int(18 * scale)
            head_radius = int(18 * scale)
        elif b_shape == "bird":
            body_radius = int(19 * scale)

        # Ciało
        pygame.draw.circle(surface, c_body, (int(center_x), int(center_y + 6 * scale)), body_radius)
        # Brzuch / Akcent
        pygame.draw.circle(surface, c_accent, (int(center_x), int(center_y + 8 * scale)), int(body_radius * 0.65))

        # Głowa
        head_y = center_y - 8 * scale
        pygame.draw.circle(surface, c_body, (int(center_x), int(head_y)), head_radius)

        # Uszy / Rogi
        ear = preset["ear_type"]
        if ear == "pointed":
            # Lewe ucho
            e1 = [(center_x - 16 * scale, head_y - 8 * scale),
                  (center_x - 12 * scale, head_y - 28 * scale),
                  (center_x - 2 * scale, head_y - 14 * scale)]
            # Prawe ucho
            e2 = [(center_x + 16 * scale, head_y - 8 * scale),
                  (center_x + 12 * scale, head_y - 28 * scale),
                  (center_x + 2 * scale, head_y - 14 * scale)]
            pygame.draw.polygon(surface, c_body, e1)
            pygame.draw.polygon(surface, c_body, e2)
            # Wnętrze uszu
            pygame.draw.polygon(surface, c_accent, [(e1[0][0]+2, e1[0][1]), (e1[1][0], e1[1][1]+4), (e1[2][0]-2, e1[2][1])])
            pygame.draw.polygon(surface, c_accent, [(e2[0][0]-2, e2[0][1]), (e2[1][0], e2[1][1]+4), (e2[2][0]+2, e2[2][1])])
            if "ear_tips_black" in specials:
                pygame.draw.circle(surface, (20, 20, 25), (int(e1[1][0]), int(e1[1][1])), int(3 * scale))
                pygame.draw.circle(surface, (20, 20, 25), (int(e2[1][0]), int(e2[1][1])), int(3 * scale))

        elif ear == "bear_round" or ear == "rounded":
            pygame.draw.circle(surface, c_body, (int(center_x - 16 * scale), int(head_y - 16 * scale)), int(8 * scale))
            pygame.draw.circle(surface, c_body, (int(center_x + 16 * scale), int(head_y - 16 * scale)), int(8 * scale))
            pygame.draw.circle(surface, c_accent, (int(center_x - 16 * scale), int(head_y - 16 * scale)), int(4 * scale))
            pygame.draw.circle(surface, c_accent, (int(center_x + 16 * scale), int(head_y - 16 * scale)), int(4 * scale))

        elif ear == "long_rabbit":
            # Uszy królika
            r1 = pygame.Rect(center_x - 15 * scale, head_y - 36 * scale, 10 * scale, 24 * scale)
            r2 = pygame.Rect(center_x + 5 * scale, head_y - 36 * scale, 10 * scale, 24 * scale)
            pygame.draw.ellipse(surface, c_body, r1)
            pygame.draw.ellipse(surface, c_body, r2)
            pygame.draw.ellipse(surface, (245, 170, 190), r1.inflate(-4 * scale, -6 * scale))
            pygame.draw.ellipse(surface, (245, 170, 190), r2.inflate(-4 * scale, -6 * scale))

        elif ear == "floppy":
            pygame.draw.ellipse(surface, c_body, (center_x - 24 * scale, head_y - 10 * scale, 12 * scale, 24 * scale))
            pygame.draw.ellipse(surface, c_body, (center_x + 12 * scale, head_y - 10 * scale, 12 * scale, 24 * scale))

        elif ear == "horns" or "horns" in specials or "antlers" in specials:
            # Rogi
            pygame.draw.line(surface, (220, 200, 160), (center_x - 10 * scale, head_y - 12 * scale), (center_x - 20 * scale, head_y - 28 * scale), int(4 * scale))
            pygame.draw.line(surface, (220, 200, 160), (center_x + 10 * scale, head_y - 12 * scale), (center_x + 20 * scale, head_y - 28 * scale), int(4 * scale))
            if "antlers" in specials or "crystal_antlers" in specials:
                horn_c = (140, 220, 255) if "crystal_antlers" in specials else (180, 140, 90)
                pygame.draw.line(surface, horn_c, (center_x - 15 * scale, head_y - 20 * scale), (center_x - 26 * scale, head_y - 22 * scale), int(3 * scale))
                pygame.draw.line(surface, horn_c, (center_x + 15 * scale, head_y - 20 * scale), (center_x + 26 * scale, head_y - 22 * scale), int(3 * scale))

        # Cechy specjalne głowy (Łatki pandy, grzywa lwa itp.)
        if "panda_patches" in specials:
            pygame.draw.circle(surface, (30, 30, 35), (int(center_x - 8 * scale), int(head_y - 2 * scale)), int(7 * scale))
            pygame.draw.circle(surface, (30, 30, 35), (int(center_x + 8 * scale), int(head_y - 2 * scale)), int(7 * scale))
        elif "lion_mane" in specials:
            pygame.draw.circle(surface, (180, 100, 30), (int(center_x), int(head_y)), int( head_radius + 7 * scale), int(6 * scale))

        # Oczy (Z mruganiem i blaskiem)
        eye_y = head_y - 2 * scale
        eye_dist = 8 * scale
        if blink:
            pygame.draw.line(surface, (20, 20, 20), (center_x - eye_dist - 3 * scale, eye_y), (center_x - eye_dist + 3 * scale, eye_y), int(2 * scale))
            pygame.draw.line(surface, (20, 20, 20), (center_x + eye_dist - 3 * scale, eye_y), (center_x + eye_dist + 3 * scale, eye_y), int(2 * scale))
        else:
            e_size = int(5 * scale)
            if "big_frog_eyes" in specials or "360_eyes" in specials:
                e_size = int(7 * scale)
            # Białko / Kolor tęczówki
            pygame.draw.circle(surface, c_eye, (int(center_x - eye_dist), int(eye_y)), e_size)
            pygame.draw.circle(surface, c_eye, (int(center_x + eye_dist), int(eye_y)), e_size)
            # Źrenica
            pygame.draw.circle(surface, (15, 15, 20), (int(center_x - eye_dist), int(eye_y)), int(e_size * 0.6))
            pygame.draw.circle(surface, (15, 15, 20), (int(center_x + eye_dist), int(eye_y)), int(e_size * 0.6))
            # Błysk w oku
            pygame.draw.circle(surface, (255, 255, 255), (int(center_x - eye_dist - 1.5 * scale), int(eye_y - 1.5 * scale)), int(1.5 * scale))
            pygame.draw.circle(surface, (255, 255, 255), (int(center_x + eye_dist - 1.5 * scale), int(eye_y - 1.5 * scale)), int(1.5 * scale))

        # Pyszczek / Dziób
        snout = preset["snout_type"]
        snout_y = head_y + 6 * scale
        if "beak" in snout:
            b_color = (245, 160, 40)
            if snout == "beak_toucan":
                b_color = (250, 180, 30)
                pygame.draw.polygon(surface, b_color, [
                    (center_x - 6 * scale, snout_y - 2 * scale),
                    (center_x + 6 * scale, snout_y - 2 * scale),
                    (center_x, snout_y + 12 * scale)
                ])
            else:
                pygame.draw.polygon(surface, b_color, [
                    (center_x - 5 * scale, snout_y),
                    (center_x + 5 * scale, snout_y),
                    (center_x, snout_y + 6 * scale)
                ])
        elif snout == "pig_snout":
            pygame.draw.ellipse(surface, (245, 140, 160), (center_x - 6 * scale, snout_y - 2 * scale, 12 * scale, 8 * scale))
            pygame.draw.circle(surface, (180, 80, 100), (int(center_x - 2.5 * scale), int(snout_y + 2 * scale)), int(1.5 * scale))
            pygame.draw.circle(surface, (180, 80, 100), (int(center_x + 2.5 * scale), int(snout_y + 2 * scale)), int(1.5 * scale))
        else:
            # Nosek zwierzęcy (kot, pies, lis, niedźwiedź)
            n_color = (30, 25, 25)
            if "big_black_nose" in specials:
                pygame.draw.ellipse(surface, n_color, (center_x - 6 * scale, snout_y - 3 * scale, 12 * scale, 9 * scale))
            else:
                pygame.draw.polygon(surface, n_color, [
                    (center_x - 3.5 * scale, snout_y),
                    (center_x + 3.5 * scale, snout_y),
                    (center_x, snout_y + 3.5 * scale)
                ])
                # Buźka
                pygame.draw.line(surface, n_color, (center_x, snout_y + 3.5 * scale), (center_x, snout_y + 6 * scale), int(1.5 * scale))
                pygame.draw.line(surface, n_color, (center_x - 3 * scale, snout_y + 7.5 * scale), (center_x, snout_y + 6 * scale), int(1.5 * scale))
                pygame.draw.line(surface, n_color, (center_x + 3 * scale, snout_y + 7.5 * scale), (center_x, snout_y + 6 * scale), int(1.5 * scale))

        # Wąsy (jeśli występują)
        if "whiskers" in specials:
            w_y = snout_y + 2 * scale
            pygame.draw.line(surface, (40, 40, 40), (center_x - 6 * scale, w_y), (center_x - 18 * scale, w_y - 3 * scale), int(1.5 * scale))
            pygame.draw.line(surface, (40, 40, 40), (center_x - 6 * scale, w_y + 2 * scale), (center_x - 17 * scale, w_y + 3 * scale), int(1.5 * scale))
            pygame.draw.line(surface, (40, 40, 40), (center_x + 6 * scale, w_y), (center_x + 18 * scale, w_y - 3 * scale), int(1.5 * scale))
            pygame.draw.line(surface, (40, 40, 40), (center_x + 6 * scale, w_y + 2 * scale), (center_x + 17 * scale, w_y + 3 * scale), int(1.5 * scale))

        # Akcesoria / Dodatki
        if accessory and accessory != "Brak":
            acc_y = head_y - 18 * scale
            if accessory == "Kapelusz Maga":
                # Stożek
                pygame.draw.polygon(surface, (60, 40, 110), [
                    (center_x - 14 * scale, acc_y + 4 * scale),
                    (center_x + 14 * scale, acc_y + 4 * scale),
                    (center_x, acc_y - 24 * scale)
                ])
                # Rondo
                pygame.draw.ellipse(surface, (45, 30, 85), (center_x - 18 * scale, acc_y + 1 * scale, 36 * scale, 8 * scale))
                # Gwiazdka
                pygame.draw.circle(surface, (245, 210, 60), (int(center_x), int(acc_y - 8 * scale)), int(3 * scale))

            elif accessory == "Złota Korona":
                c_pts = [
                    (center_x - 14 * scale, acc_y + 4 * scale),
                    (center_x - 14 * scale, acc_y - 8 * scale),
                    (center_x - 7 * scale, acc_y - 2 * scale),
                    (center_x, acc_y - 12 * scale),
                    (center_x + 7 * scale, acc_y - 2 * scale),
                    (center_x + 14 * scale, acc_y - 8 * scale),
                    (center_x + 14 * scale, acc_y + 4 * scale),
                ]
                pygame.draw.polygon(surface, (240, 195, 40), c_pts)
                pygame.draw.polygon(surface, (200, 155, 20), c_pts, int(1.5 * scale))

            elif accessory == "Korona Kwiatowa":
                colors = [(240, 90, 120), (250, 210, 60), (120, 210, 240), (230, 140, 220)]
                for i in range(5):
                    fx = center_x - 14 * scale + i * 7 * scale
                    fy = acc_y + 4 * scale + (math.sin(i * 1.5) * 2 * scale)
                    pygame.draw.circle(surface, colors[i % len(colors)], (int(fx), int(fy)), int(4 * scale))
                    pygame.draw.circle(surface, (255, 255, 255), (int(fx), int(fy)), int(1.5 * scale))

            elif accessory == "Czerwona Kokarda":
                kx = center_x + 12 * scale
                ky = head_y - 14 * scale
                pygame.draw.polygon(surface, (220, 45, 55), [(kx, ky), (kx - 8 * scale, ky - 5 * scale), (kx - 8 * scale, ky + 5 * scale)])
                pygame.draw.polygon(surface, (220, 45, 55), [(kx, ky), (kx + 8 * scale, ky - 5 * scale), (kx + 8 * scale, ky + 5 * scale)])
                pygame.draw.circle(surface, (170, 30, 40), (int(kx), int(ky)), int(3 * scale))

            elif accessory == "Okulary Przeciwsłoneczne":
                gy = head_y - 2 * scale
                pygame.draw.rect(surface, (20, 20, 25), (center_x - 14 * scale, gy - 4 * scale, 12 * scale, 8 * scale), border_radius=2)
                pygame.draw.rect(surface, (20, 20, 25), (center_x + 2 * scale, gy - 4 * scale, 12 * scale, 8 * scale), border_radius=2)
                pygame.draw.line(surface, (20, 20, 25), (center_x - 2 * scale, gy - 1 * scale), (center_x + 2 * scale, gy - 1 * scale), int(2 * scale))

            elif accessory == "Zielony Liść":
                ly = head_y - 16 * scale
                pygame.draw.ellipse(surface, (80, 190, 70), (center_x - 4 * scale, ly - 8 * scale, 14 * scale, 8 * scale))
                pygame.draw.line(surface, (40, 120, 35), (center_x, ly), (center_x + 8 * scale, ly - 4 * scale), int(1.5 * scale))
