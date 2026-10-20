"""Connexion Wi-Fi et recuperation de la position ISS."""

import network
import time
import urequests

try:
    import ujson as json
except ImportError:
    import json

from settings import API_URL, WIFI_TIMEOUT_MS, HTTP_TIMEOUT_S


def connect_wifi(ssid, password):
    """Connexion Wi-Fi avec reutilisation de la connexion existante."""

    try:
        station = network.WLAN(network.WLAN.IF_STA)
    except AttributeError:
        station = network.WLAN(network.STA_IF)

    station.active(True)

    # Si le Wi-Fi fonctionne deja, on garde la connexion.
    if station.isconnected():
        return station

    print("Connexion Wi-Fi...")

    try:
        station.connect(ssid, password)
    except OSError as error:
        print("Premiere tentative Wi-Fi :", error)

        # Reset du Wi-Fi seulement si connect() echoue vraiment.
        station.active(False)
        time.sleep_ms(1000)

        station.active(True)
        time.sleep_ms(1000)

        station.connect(ssid, password)

    start = time.ticks_ms()

    while not station.isconnected():
        elapsed = time.ticks_diff(time.ticks_ms(), start)

        if elapsed >= WIFI_TIMEOUT_MS:
            raise OSError("Connexion Wi-Fi indisponible")

        time.sleep_ms(500)

    print("Wi-Fi connecte :", station.ifconfig()[0])

    return station


def parse_position(payload):
    """Verifier et convertir les coordonnees de l'ISS."""

    if not isinstance(payload, dict):
        raise ValueError("Reponse API invalide")

    if payload.get("message") != "success":
        raise ValueError("Reponse API sans succes")

    position = payload.get("iss_position")

    if not isinstance(position, dict):
        raise ValueError("Champ iss_position absent")

    try:
        latitude = float(position["latitude"])
        longitude = float(position["longitude"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("Coordonnees invalides")

    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude hors limites")

    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude hors limites")

    return latitude, longitude


def get_iss_position():
    """Recuperer la position actuelle de l'ISS."""

    response = None

    try:
        response = urequests.get(API_URL, timeout=HTTP_TIMEOUT_S)

        if response.status_code != 200:
            raise ValueError("Erreur HTTP %s" % response.status_code)

        body = response.text

        if not body:
            raise ValueError("Reponse API vide")

        data = json.loads(body)

        return parse_position(data)

    finally:
        if response is not None:
            response.close()
