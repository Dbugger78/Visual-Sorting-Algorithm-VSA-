import random
import pygame
import numpy

from algorithms import bubble_sort, quick_sort, merge_sort
from bars import (draw_bars, draw_text, draw_panel_label, draw_banner,
                  BACKGROUND, TEXT_COLOR)

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
pygame.mixer.set_num_channels(16)

WINDOW_SIZE = (1200, 700)
fullscreen = False
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
pygame.display.set_caption("Sorting Race")
clock = pygame.time.Clock()

big_font = None
small_font = None
font_height_used = 0


def update_fonts(height):
    """Rebuild the fonts whenever the screen height changes."""
    global big_font, small_font, font_height_used
    if height != font_height_used:
        big_font = pygame.font.SysFont("arial", max(18, height // 30))
        small_font = pygame.font.SysFont("arial", max(14, height // 48))
        font_height_used = height


def toggle_fullscreen():
    global screen, fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)


# key -> (list size, steps per frame)
SIZES = {
    pygame.K_1: (20, 1),
    pygame.K_2: (100, 5),
    pygame.K_3: (500, 50),
    pygame.K_4: (2000, 500),
}

ALGORITHMS = [("Bubble Sort", bubble_sort),
              ("Quick Sort", quick_sort),
              ("Merge Sort", merge_sort)]

# ---------- sound ----------
TONE_COUNT = 40
tone_cache = {}


def get_tone(bucket):
    """Make a short sine beep. Cached so we only build each pitch once."""
    if bucket not in tone_cache:
        mixer_rate, mixer_format, mixer_channels = pygame.mixer.get_init()
        frequency = 200 + bucket * 25
        length = int(mixer_rate * 0.04)
        times = numpy.arange(length) / mixer_rate
        wave = numpy.sin(2 * numpy.pi * frequency * times)
        fade = numpy.linspace(1, 0, length)  # fade out to avoid clicks
        samples = (wave * fade * 3000).astype(numpy.int16)

        if mixer_channels == 2:
            samples = numpy.column_stack((samples, samples))

        tone_cache[bucket] = pygame.sndarray.make_sound(samples)
    return tone_cache[bucket]


# ---------- race setup ----------
def make_race(size):
    starting_numbers = random.sample(range(1, size + 1), size)
    racers = []
    for name, sort_function in ALGORITHMS:
        numbers = starting_numbers.copy()  # everyone gets the same data
        racers.append({
            "name": name,
            "numbers": numbers,
            "generator": sort_function(numbers),
            "active": (),
            "steps": 0,
            "finished_time": None,
        })
    return racers


size = 100
steps_per_frame = 5
racers = make_race(size)
running = False
start_time = 0
winner = None
sound_on = True

# ---------- main loop ----------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key in SIZES:
                size, steps_per_frame = SIZES[event.key]
                racers = make_race(size)
                running = False
                winner = None
            elif event.key == pygame.K_r:
                racers = make_race(size)
                running = False
                winner = None
            elif event.key == pygame.K_SPACE and not running and winner is None:
                running = True
                start_time = pygame.time.get_ticks()
            elif event.key == pygame.K_UP:
                steps_per_frame *= 2
            elif event.key == pygame.K_DOWN:
                steps_per_frame = max(1, steps_per_frame // 2)
            elif event.key == pygame.K_m:
                sound_on = not sound_on
            elif event.key == pygame.K_f:
                toggle_fullscreen()
            elif event.key == pygame.K_ESCAPE and fullscreen:
                toggle_fullscreen()

    # advance every racer by the same number of steps
    if running:
        for racer in racers:
            if racer["finished_time"] is not None:
                continue

            for _ in range(steps_per_frame):
                try:
                    racer["active"] = next(racer["generator"])
                    racer["steps"] += 1
                except StopIteration:
                    racer["active"] = ()
                    racer["finished_time"] = pygame.time.get_ticks() - start_time
                    if winner is None:
                        winner = racer["name"]
                    break

            # one beep per racer per frame, pitch based on bar height
            if sound_on and racer["active"]:
                value = racer["numbers"][racer["active"][0]]
                bucket = int(value / size * (TONE_COUNT - 1))
                get_tone(bucket).play()

        if all(r["finished_time"] is not None for r in racers):
            running = False

    # ---------- layout (worked out from the current screen size) ----------
    width, height = screen.get_size()
    update_fonts(height)
    big_h = big_font.get_height()
    small_h = small_font.get_height()

    margin = width * 0.04
    gap = width * 0.03
    panel_width = (width - 2 * margin - 2 * gap) / 3

    title_y = height * 0.015
    hints_y = title_y + big_h + 4
    info_y = hints_y + small_h + 4
    panel_top = info_y + small_h + big_h + 20          # room for panel names
    panel_bottom = height - (3 * big_h + 40)            # room for stats + banner
    panel_height = panel_bottom - panel_top
    banner_y = height - big_h - 12

    # ---------- drawing ----------
    screen.fill(BACKGROUND)
    draw_text(screen, big_font, "SORTING RACE", (margin, title_y))
    draw_text(screen, small_font,
              "1-4: size (20/100/500/2000)   SPACE: start   R: reset   "
              "UP/DOWN: speed   M: sound   F: fullscreen",
              (margin, hints_y), TEXT_COLOR)
    draw_text(screen, small_font,
              "Items: " + str(size) + "   Steps/frame: " + str(steps_per_frame),
              (margin, info_y), TEXT_COLOR)

    for position in range(len(racers)):
        racer = racers[position]
        left = margin + position * (panel_width + gap)
        area = (left, panel_top, panel_width, panel_height)

        draw_bars(screen, area, racer["numbers"], racer["active"], size,
                  racer["finished_time"] is not None)
        draw_panel_label(screen, big_font, area, racer["name"],
                         racer["steps"], racer["finished_time"])

    if winner is not None:
        draw_banner(screen, big_font, "Winner: " + winner, width // 2, banner_y)

    pygame.display.flip()
    clock.tick(60)
