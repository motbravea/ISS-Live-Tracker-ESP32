"""Suivi de la Station Spatiale Internationale."""

import time
import gc

from settings import POLL_INTERVAL_MS
from iss_api import connect_wifi, get_iss_position
from display import init_display, update_display, show_status


def main():

    print("1 - ESP32 pret")
    print("2 - main.py charge")

    try:
        from config import WIFI_SSID, WIFI_PASSWORD

    except ImportError:
        print("Erreur : config.py absent")
        return

    if not WIFI_SSID:
        print("Erreur : WIFI_SSID vide")
        return

    oled = None

    while True:
        cycle_start = time.ticks_ms()
        stage = "OLED"

        try:
            # Initialiser l'ecran une seule fois.
            if oled is None:
                oled = init_display()
                show_status(oled, "Demarrage...", "Connexion Wi-Fi")

            # WIFI
            stage = "Wi-Fi"
            connect_wifi(WIFI_SSID, WIFI_PASSWORD)

            # API ISS
            stage = "API"
            cycle_start = time.ticks_ms()
            latitude, longitude = get_iss_position()

            # OLED
            stage = "OLED"
            x, y = update_display(oled, latitude, longitude)

            print(
                "t=%d ms | lat=%.4f lon=%.4f | pixel=(%d,%d)"
                % (
                    cycle_start,
                    latitude,
                    longitude,
                    x,
                    y
                )
            )

        except Exception as error:
            print("Erreur %s : %s" % (stage, error))

            if stage == "OLED":
                oled = None

            elif oled is not None:
                try:
                    show_status(oled, stage + " indisponible")
                except Exception:
                    oled = None

        finally:
            gc.collect()

            elapsed = time.ticks_diff(time.ticks_ms(), cycle_start)
            waiting = max(0, POLL_INTERVAL_MS - elapsed)
            time.sleep_ms(waiting)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("Programme arrete depuis Thonny.")
