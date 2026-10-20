"""Gestion de l'ecran OLED, de la carte et du marqueur ISS."""

from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C

from settings import (
    SDA_PIN,
    SCL_PIN,
    I2C_FREQ,
    OLED_ADDRESS,
    WIDTH,
    HEIGHT
)

from world_map import CONTINENTS


def init_display():
    """Initialiser l'ecran OLED."""

    i2c = SoftI2C(
        sda=Pin(SDA_PIN),
        scl=Pin(SCL_PIN),
        freq=I2C_FREQ
    )

    addresses = i2c.scan()

    print(
        "Adresses I2C :",
        [hex(address) for address in addresses]
    )

    if OLED_ADDRESS not in addresses:
        raise OSError(
            "OLED absent : verifier 3V3, GND, SDA et SCL"
        )

    oled = SSD1306_I2C(
        WIDTH,
        HEIGHT,
        i2c,
        addr=OLED_ADDRESS
    )

    return oled


def coordinates_to_pixels(latitude, longitude):
    """Transformer latitude/longitude en pixels."""

    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude hors limites")

    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude hors limites")

    x = int((longitude + 180) * WIDTH / 360)
    y = int((90 - latitude) * HEIGHT / 180)

    x = max(0, min(WIDTH - 1, x))
    y = max(0, min(HEIGHT - 1, y))

    return x, y


def draw_map(oled):
    """Dessiner les continents."""

    for contour in CONTINENTS:
        points = []

        for longitude, latitude in contour:
            x, y = coordinates_to_pixels(latitude, longitude)
            points.append((x, y))

        for index in range(len(points)):
            x1, y1 = points[index]
            x2, y2 = points[(index + 1) % len(points)]
            oled.line(x1, y1, x2, y2, 1)


def draw_marker(oled, x, y):
    """Dessiner un gros X visible pour l'ISS."""

    # Effacer une petite zone autour du X pour garder un bon contraste.
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            px = x + dx
            py = y + dy

            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                oled.pixel(px, py, 0)

    # Grand X blanc 7x7.
    for offset in range(-3, 4):
        x1 = x + offset
        y1 = y + offset

        x2 = x + offset
        y2 = y - offset

        if 0 <= x1 < WIDTH and 0 <= y1 < HEIGHT:
            oled.pixel(x1, y1, 1)

        if 0 <= x2 < WIDTH and 0 <= y2 < HEIGHT:
            oled.pixel(x2, y2, 1)

    # Centre du marqueur.
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        oled.pixel(x, y, 1)


def update_display(oled, latitude, longitude):
    """Afficher la carte et la position ISS."""

    x, y = coordinates_to_pixels(latitude, longitude)

    oled.fill(0)
    draw_map(oled)
    draw_marker(oled, x, y)
    oled.show()

    return x, y


def show_status(oled, first_line, second_line="Nouvel essai..."):
    """Afficher un message d'etat."""

    oled.fill(0)
    oled.text("SUIVI ISS", 0, 0, 1)
    oled.text(first_line[:16], 0, 24, 1)
    oled.text(second_line[:16], 0, 40, 1)
    oled.show()
