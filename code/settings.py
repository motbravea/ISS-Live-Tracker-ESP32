"""Parametres techniques communs."""

API_URL = "http://api.open-notify.org/iss-now.json"

# Minimum 3 secondes entre les appels API
POLL_INTERVAL_MS = 3000

# Plus de temps pour le Wi-Fi du college
WIFI_TIMEOUT_MS = 30000

# Plus tolerant si l'API est lente
HTTP_TIMEOUT_S = 10

# ESP32 + OLED SSD1306
SDA_PIN = 21
SCL_PIN = 22
I2C_FREQ = 100000

# OLED detecte a l'adresse 0x3C
OLED_ADDRESS = 0x3C

WIDTH = 128
HEIGHT = 64
