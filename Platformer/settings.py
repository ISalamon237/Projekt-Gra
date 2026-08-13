import pygame

# Ekran i Klatki na sekundę
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Gniazdo Gracza & Leśna Przygoda"

# Kolory - Paleta Natury i Ciemnego Motywu
COLOR_BG = (28, 22, 18)
COLOR_PANEL_BG = (42, 33, 26)
COLOR_PANEL_BORDER = (84, 66, 48)
COLOR_ACCENT = (212, 143, 56)
COLOR_ACCENT_HOVER = (235, 168, 78)
COLOR_TEXT = (245, 238, 225)
COLOR_TEXT_MUTED = (165, 150, 135)
COLOR_SUCCESS = (100, 180, 90)
COLOR_SHADOW = (0, 0, 0, 80)

# Kategorię zwierząt
CAT_ALL = "Wszystkie"
CAT_MAMMALS = "Ssaki"
CAT_BIRDS = "Ptaki"
CAT_REPTILES = "Gady i Płazy"
CAT_MYTHICAL = "Stworzenia Baśniowe"

CATEGORIES = [CAT_ALL, CAT_MAMMALS, CAT_BIRDS, CAT_REPTILES, CAT_MYTHICAL]

# Dodatki / Akcesoria
ACCESSORIES = [
    "Brak",
    "Kapelusz Maga",
    "Korona Kwiatowa",
    "Czerwona Kokarda",
    "Okulary Przeciwsłoneczne",
    "Opaska Leśna",
    "Złota Korona",
    "Zielony Liść",
]

# Stany Gry
STATE_CUSTOMIZATION = "CUSTOMIZATION"
STATE_NEST = "NEST"
STATE_FOREST = "FOREST"
STATE_ARENA = "ARENA"
STATE_DUNGEON = "DUNGEON"

# Czas Wyzwania (w sekundach)
ARENA_DURATION = 60.0   # 1 minuta na zbieranie jedzenia
RUSH_DURATION = 60.0    # 1 minuta na dotarcie do lochu


# Rozmiar Siatki i Fizyki
TILE_SIZE = 48
PLAYER_SPEED = 4.0

