import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    TITLE,
    STATE_CUSTOMIZATION,
    STATE_NEST,
    STATE_FOREST,
    STATE_ARENA,
    STATE_DUNGEON,
)
from player import Player
from sound_manager import SoundManager
from customization_menu import CustomizationMenu
from nest_scene import NestScene
from forest_scene import ForestScene
from arena_scene import ArenaScene
from dungeon_scene import DungeonScene


class Game:
    """Główna klasa zarządcy pętli gry i scen."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Zarządca dźwięków
        self.sound_manager = SoundManager()

        # Tworzenie postaci Gracza (domyślnie lis w gnieździe)
        self.player = Player(x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2 + 40, name="Bohater", animal_id="fox")

        # Inicjalizacja scen
        self.state = STATE_CUSTOMIZATION
        self.customization_menu = CustomizationMenu(
            player=self.player,
            sound_manager=self.sound_manager,
            on_finish_callback=self._go_to_nest,
        )
        self.nest_scene = NestScene(
            player=self.player,
            sound_manager=self.sound_manager,
            on_open_mirror_cb=self._go_to_customization,
            on_exit_to_forest_cb=self._go_to_forest,
            on_start_play_cb=self._start_play_challenge,
        )
        self.forest_scene = ForestScene(
            player=self.player,
            sound_manager=self.sound_manager,
            on_return_to_nest_cb=self._go_to_nest,
        )
        self.arena_scene = ArenaScene(
            player=self.player,
            sound_manager=self.sound_manager,
            on_enter_dungeon_cb=self._go_to_dungeon,
            on_cancel_cb=self._go_to_nest,
        )
        self.dungeon_scene = DungeonScene(
            player=self.player,
            sound_manager=self.sound_manager,
            on_victory_cb=self._go_to_nest,
        )

    def _go_to_nest(self):
        self.state = STATE_NEST
        self.player.x = SCREEN_WIDTH // 2
        self.player.y = SCREEN_HEIGHT // 2 + 40

    def _go_to_customization(self):
        self.state = STATE_CUSTOMIZATION
        self.customization_menu.name_input.text = self.player.name

    def _go_to_forest(self):
        self.state = STATE_FOREST
        self.forest_scene.enter_forest()


    def _start_play_challenge(self):
        self.state = STATE_ARENA
        self.arena_scene.start_challenge()

    def _go_to_dungeon(self):
        self.state = STATE_DUNGEON
        self.dungeon_scene.start_dungeon()


    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                if self.state == STATE_CUSTOMIZATION:
                    self.customization_menu.handle_event(event)
                elif self.state == STATE_NEST:
                    self.nest_scene.handle_event(event)
                elif self.state == STATE_FOREST:
                    self.forest_scene.handle_event(event)
                elif self.state == STATE_ARENA:
                    self.arena_scene.handle_event(event)
                elif self.state == STATE_DUNGEON:
                    self.dungeon_scene.handle_event(event)

            # Aktualizacja logiki w zależności od stanu
            if self.state == STATE_CUSTOMIZATION:
                self.customization_menu.update(dt)
            elif self.state == STATE_NEST:
                self.nest_scene.update(dt, keys)
            elif self.state == STATE_FOREST:
                self.forest_scene.update(dt, keys)
            elif self.state == STATE_ARENA:
                self.arena_scene.update(dt, keys)
            elif self.state == STATE_DUNGEON:
                self.dungeon_scene.update(dt, keys)

            # Rysowanie
            if self.state == STATE_CUSTOMIZATION:
                self.customization_menu.draw(self.screen)
            elif self.state == STATE_NEST:
                self.nest_scene.draw(self.screen)
            elif self.state == STATE_FOREST:
                self.forest_scene.draw(self.screen)
            elif self.state == STATE_ARENA:
                self.arena_scene.draw(self.screen)
            elif self.state == STATE_DUNGEON:
                self.dungeon_scene.draw(self.screen)

            pygame.display.flip()


        pygame.quit()
