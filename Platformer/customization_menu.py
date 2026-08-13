import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BG,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    CATEGORIES,
    CAT_ALL,
    ACCESSORIES,
)
from animal_presets import ANIMAL_PRESETS, ANIMAL_BY_ID
from animal_renderer import AnimalRenderer
from ui import Button, TextInput, CategoryTab, AnimalCard, ColorSwatchPicker


class CustomizationMenu:
    """Menu wyboru wyglądu postaci z 50 zwierząt, kolorów, dodatków i imienia."""

    def __init__(self, player, sound_manager, on_finish_callback):
        self.player = player
        self.sound_manager = sound_manager
        self.on_finish_callback = on_finish_callback

        self.font_title = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 16)
        self.font_section = pygame.font.SysFont("Arial", 18, bold=True)

        # Pole imienia
        self.name_input = TextInput((50, 90, 280, 44), default_text=self.player.name)

        # Wybrany gatunek i kolory
        self.selected_preset = ANIMAL_BY_ID.get(self.player.animal_id, ANIMAL_PRESETS[0])
        self.color_body = list(self.player.color_body)
        self.color_accent = list(self.player.color_accent)
        self.color_eye = list(self.player.color_eye)
        self.accessory_idx = ACCESSORIES.index(self.player.accessory) if self.player.accessory in ACCESSORIES else 0

        # Kategoria
        self.selected_category = CAT_ALL
        self.category_tabs = []
        self._init_category_tabs()

        # Stronicowanie siatki zwierząt
        self.page = 0
        self.items_per_page = 12 # 4 kolumny x 3 wiersze
        self.filtered_presets = []
        self.animal_cards = []
        self._update_filtered_presets()

        # Wybór kolorów
        self.picker_body = ColorSwatchPicker(
            50, 520, "Futerko/Tułów:", tuple(self.color_body), self._on_body_color_change
        )
        self.picker_accent = ColorSwatchPicker(
            50, 580, "Brzuch/Akcent:", tuple(self.color_accent), self._on_accent_color_change
        )

        # Przycisk dodatku
        self.btn_acc = Button(
            (50, 640, 280, 38),
            f"Dodatek: {ACCESSORIES[self.accessory_idx]}",
            callback=self._cycle_accessory,
            color=(55, 42, 32),
            hover_color=(75, 58, 45),
            font_size=16
        )

        # Przycisk Strona Poprzednia/Następna
        self.btn_prev_page = Button((400, 640, 110, 38), "< Poprzednie", callback=self._prev_page, font_size=15)
        self.btn_next_page = Button((860, 640, 110, 38), "Następne >", callback=self._next_page, font_size=15)

        # Przycisk zatwierdzenia
        self.btn_submit = Button(
            (SCREEN_WIDTH - 260, SCREEN_HEIGHT - 70, 220, 48),
            "Rozpocznij w Gnieździe",
            callback=self._submit,
            color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            font_size=18,
        )

        self.anim_time = 0.0

    def _init_category_tabs(self):
        self.category_tabs = []
        x = 400
        for cat in CATEGORIES:
            tab = CategoryTab(
                (x, 90, 115, 34),
                cat,
                is_selected=(cat == self.selected_category),
                callback=lambda c=cat: self._select_category(c),
            )
            self.category_tabs.append(tab)
            x += 122

    def _select_category(self, category):
        self.selected_category = category
        self.sound_manager.play("click")
        self.page = 0
        for tab in self.category_tabs:
            tab.is_selected = (tab.text == category)
        self._update_filtered_presets()

    def _update_filtered_presets(self):
        if self.selected_category == CAT_ALL:
            self.filtered_presets = ANIMAL_PRESETS
        else:
            self.filtered_presets = [p for p in ANIMAL_PRESETS if p["category"] == self.selected_category]

        self._rebuild_cards()

    def _rebuild_cards(self):
        self.animal_cards = []
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.filtered_presets))
        page_items = self.filtered_presets[start_idx:end_idx]

        for i, preset in enumerate(page_items):
            col = i % 4
            row = i // 4
            x = 400 + col * 140
            y = 140 + row * 160
            card = AnimalCard(
                (x, y, 130, 150),
                preset,
                is_selected=(preset["id"] == self.selected_preset["id"]),
                callback=lambda p=preset: self._select_animal(p),
            )
            self.animal_cards.append(card)

    def _select_animal(self, preset):
        self.selected_preset = preset
        self.color_body = list(preset["color_body"])
        self.color_accent = list(preset["color_accent"])
        self.color_eye = list(preset["color_eye"])
        self.picker_body.current_color = tuple(self.color_body)
        self.picker_accent.current_color = tuple(self.color_accent)
        self.sound_manager.play("select")

        for card in self.animal_cards:
            card.is_selected = (card.preset["id"] == preset["id"])

    def _prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.sound_manager.play("click")
            self._rebuild_cards()

    def _next_page(self):
        max_page = (len(self.filtered_presets) - 1) // self.items_per_page
        if self.page < max_page:
            self.page += 1
            self.sound_manager.play("click")
            self._rebuild_cards()

    def _on_body_color_change(self, color):
        self.color_body = list(color)
        self.sound_manager.play("click")

    def _on_accent_color_change(self, color):
        self.color_accent = list(color)
        self.sound_manager.play("click")

    def _cycle_accessory(self):
        self.accessory_idx = (self.accessory_idx + 1) % len(ACCESSORIES)
        self.btn_acc.text = f"Dodatek: {ACCESSORIES[self.accessory_idx]}"
        self.sound_manager.play("click")

    def _submit(self):
        player_name = self.name_input.text.strip() if self.name_input.text.strip() else "Bohater"
        self.player.customize(
            name=player_name,
            animal_id=self.selected_preset["id"],
            color_body=tuple(self.color_body),
            color_accent=tuple(self.color_accent),
            color_eye=tuple(self.color_eye),
            accessory=ACCESSORIES[self.accessory_idx],
        )
        self.sound_manager.play("mirror")
        if self.on_finish_callback:
            self.on_finish_callback()

    def handle_event(self, event):
        self.name_input.handle_event(event)
        for tab in self.category_tabs:
            tab.handle_event(event)
        for card in self.animal_cards:
            card.handle_event(event)

        self.picker_body.handle_event(event)
        self.picker_accent.handle_event(event)
        self.btn_acc.handle_event(event)
        self.btn_prev_page.handle_event(event)
        self.btn_next_page.handle_event(event)
        self.btn_submit.handle_event(event)

    def update(self, dt):
        self.anim_time += dt
        self.name_input.update(dt)
        for card in self.animal_cards:
            card.update(dt)

    def draw(self, surface):
        surface.fill(COLOR_BG)

        # Nagłówek
        title_surf = self.font_title.render("KREATOR POSTACI ZWIERZĘCIA", True, COLOR_TEXT)
        surface.blit(title_surf, (50, 25))
        sub_surf = self.font_subtitle.render("Wybierz gatunek spośród 50 zwierząt, spersonalizuj umarszczenie i nazwij postać", True, COLOR_TEXT_MUTED)
        surface.blit(sub_surf, (50, 62))

        # Lewy panel podglądu postaci
        panel_left = pygame.Rect(40, 140, 320, 360)
        pygame.draw.rect(surface, COLOR_PANEL_BG, panel_left, border_radius=12)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, panel_left, width=2, border_radius=12)

        lbl_prev = self.font_section.render(f"Podgląd: {self.selected_preset['name']}", True, COLOR_ACCENT)
        surface.blit(lbl_prev, (panel_left.x + 20, panel_left.y + 16))

        # Duży podgląd zwierzątka na żywo
        preview_x = panel_left.centerx
        preview_y = panel_left.y + 170
        AnimalRenderer.render(
            surface,
            preview_x,
            preview_y,
            self.selected_preset["id"],
            color_body=tuple(self.color_body),
            color_accent=tuple(self.color_accent),
            color_eye=tuple(self.color_eye),
            accessory=ACCESSORIES[self.accessory_idx],
            scale=2.2,
            anim_time=self.anim_time,
            is_moving=False,
        )

        # Rysowanie dodatkowych kontrolek
        self.name_input.draw(surface)
        for tab in self.category_tabs:
            tab.draw(surface)
        for card in self.animal_cards:
            card.draw(surface)

        self.picker_body.draw(surface)
        self.picker_accent.draw(surface)
        self.btn_acc.draw(surface)
        self.btn_prev_page.draw(surface)
        self.btn_next_page.draw(surface)

        # Numery stron
        max_page = (len(self.filtered_presets) - 1) // self.items_per_page + 1
        page_surf = self.font_section.render(f"Strona {self.page + 1} z {max_page}", True, COLOR_TEXT_MUTED)
        page_rect = page_surf.get_rect(center=(685, 660))
        surface.blit(page_surf, page_rect)

        self.btn_submit.draw(surface)
