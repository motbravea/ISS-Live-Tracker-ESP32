"""Essai manuel au collège, sans Wi-Fi. Arrêter main.py avant de lancer.

Les positions sont FICTIVES et servent uniquement à vérifier l'affichage.
"""

import time
from display import init_display, update_display, show_status

oled = init_display()
show_status(oled, "TEST FICTIF", "Sans appel API")
time.sleep(2)
for latitude, longitude in ((45.5017, -73.5673), (0, 0), (-33.9, 151.2), (0, 179)):
    print("TEST FICTIF :", latitude, longitude)
    update_display(oled, latitude, longitude)
    time.sleep(3)
show_status(oled, "Test termine", "Lancer main.py")
