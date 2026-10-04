import pygame

BACKGROUND = (25, 25, 35)
PANEL_COLOR = (15, 15, 22)
BAR_COLOR = (80, 160, 255)
ACTIVE_COLOR = (255, 70, 70)
DONE_COLOR = (80, 220, 120)
TEXT_COLOR = (230, 230, 240)


def draw_bars(screen, area, numbers, active, max_value, finished):
    """Draw one list of numbers as bars inside area = (x, y, width, height)."""
    x, y, width, height = area
    pygame.draw.rect(screen, PANEL_COLOR, area)

    count = len(numbers)
    bar_width = width / count
    # leave a tiny gap between bars, but only when bars are wide enough
    if bar_width > 3:
        drawn_width = bar_width - 1
    else:
        drawn_width = max(bar_width, 1)

    for index in range(count):
        bar_height = numbers[index] / max_value * height
        left = x + index * bar_width
        top = y + height - bar_height

        if finished:
            color = DONE_COLOR
        elif index in active:
            color = ACTIVE_COLOR
        else:
            color = BAR_COLOR

        pygame.draw.rect(screen, color, (left, top, drawn_width, bar_height))


def draw_text(screen, font, text, position, color=TEXT_COLOR):
    picture = font.render(text, True, color)
    screen.blit(picture, position)


def draw_panel_label(screen, font, area, name, steps, finished_time):
    """Name above the bars, step counter and time below them."""
    x, y, width, height = area
    line = font.get_height()
    draw_text(screen, font, name, (x, y - line - 8))
    draw_text(screen, font, "Steps: " + str(steps), (x, y + height + 8))

    if finished_time is not None:
        seconds = finished_time / 1000
        draw_text(screen, font, "Done in " + format(seconds, ".2f") + "s",
                  (x, y + height + 8 + line + 4), DONE_COLOR)


def draw_banner(screen, font, text, center_x, y):
    draw_text(screen, font, text, (center_x - font.size(text)[0] // 2, y), DONE_COLOR)
