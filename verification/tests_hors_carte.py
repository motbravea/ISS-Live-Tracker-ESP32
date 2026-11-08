"""Vérification sur ordinateur : aucun résultat matériel n'est simulé comme réel."""
import ast
import importlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch
from PIL import Image, ImageDraw

PROJECT = Path(__file__).resolve().parents[1]
CODE = PROJECT/'code'
sys.path.insert(0, str(CODE))

# Remplacer uniquement les interfaces matérielles pour les contrôles hors carte.
sys.modules['network'] = types.SimpleNamespace()
sys.modules['machine'] = types.SimpleNamespace(Pin=object, SoftI2C=object)
sys.modules['ssd1306'] = types.SimpleNamespace(SSD1306_I2C=object)
import iss_api
import display
import main


class Screen:
    def __init__(self):
        self.image = Image.new('1', (128,64))
        self.pen = ImageDraw.Draw(self.image)
    def fill(self, color):
        self.pen.rectangle((0,0,127,63), fill=color)
    def line(self, x1,y1,x2,y2,color):
        self.pen.line((x1,y1,x2,y2), fill=color)
    def pixel(self,x,y,color):
        assert 0 <= x < 128 and 0 <= y < 64, (x,y)
        self.image.putpixel((x,y), color)
    def show(self):
        pass
    def text(self,text,x,y,color):
        self.pen.text((x,y),text,fill=color)


class Response:
    def __init__(self, text, status_code=200):
        self.text, self.status_code, self.closed = text, status_code, False
    def close(self):
        self.closed = True


class Checks(unittest.TestCase):
    def test_syntax(self):
        for file in CODE.glob('*.py'):
            ast.parse(file.read_text(encoding='utf-8'))
    def test_projection_examples_and_extremes(self):
        cases = [((0,0),(64,32)), ((45.5017,-73.5673),(37,15)),
                 ((90,-180),(0,0)), ((-90,180),(127,63))]
        for coordinates, expected in cases:
            self.assertEqual(display.coordinates_to_pixels(*coordinates),expected)
        for lat in range(-90,91,5):
            for lon in range(-180,181,5):
                x,y=display.coordinates_to_pixels(lat,lon)
                self.assertTrue(0<=x<128 and 0<=y<64)
    def test_reject_bad_coordinates(self):
        for lat,lon in [(91,0),(0,-181),(float('nan'),0),(0,float('inf'))]:
            with self.assertRaises(ValueError):
                display.coordinates_to_pixels(lat,lon)
    def test_valid_api(self):
        response=Response(json.dumps({'message':'success', 'iss_position':
                                     {'latitude':'45.5017','longitude':'-73.5673'}}))
        with patch.object(iss_api.urequests,'get',return_value=response):
            self.assertEqual(iss_api.get_iss_position(),(45.5017,-73.5673))
        self.assertTrue(response.closed)
    def test_invalid_api_and_close(self):
        bodies=['', ' ', '<html>erreur</html>', '{}', '[]',
                '{"message":"failure"}',
                '{"message":"success","iss_position":{}}']
        for lat in ['nan','inf','91','texte',True,None]:
            bodies.append(json.dumps({'message':'success','iss_position':
                                      {'latitude':lat,'longitude':'0'}}))
        for body in bodies:
            response=Response(body)
            with patch.object(iss_api.urequests,'get',return_value=response):
                with self.assertRaises((ValueError,TypeError)):
                    iss_api.get_iss_position()
            self.assertTrue(response.closed)
        response=Response('erreur serveur',503)
        with patch.object(iss_api.urequests,'get',return_value=response):
            with self.assertRaises(ValueError): iss_api.get_iss_position()
        self.assertTrue(response.closed)
    def test_network_exception_propagates_to_loop(self):
        with patch.object(iss_api.urequests,'get',side_effect=OSError('timeout')):
            with self.assertRaises(OSError): iss_api.get_iss_position()
    def test_x_on_map_and_edges(self):
        for x,y in [(64,32),(0,0),(127,63),(0,32),(127,32),(37,15)]:
            screen=Screen()
            display.draw_map(screen)
            display.draw_marker(screen,x,y)
            # Deux diagonales en X, sans rebouclage artificiel aux bords.
            for offset in range(-3, 4):
                for px, py in ((x + offset, y + offset),
                               (x + offset, y - offset)):
                    if 0 <= px < 128 and 0 <= py < 64:
                        self.assertEqual(screen.image.getpixel((px, py)), 1)
    def test_refresh_erases_old_marker(self):
        first,fresh=Screen(),Screen()
        display.update_display(first,45.5017,-73.5673)
        display.update_display(first,-33.9,151.2)
        display.update_display(fresh,-33.9,151.2)
        self.assertEqual(first.image.tobytes(),fresh.image.tobytes())
    def test_poll_interval_after_slow_wifi_and_api_failure(self):
        class Clock:
            now=0
            def ticks_ms(self): return self.now
            def ticks_diff(self,a,b): return a-b
            def sleep_ms(self,ms): self.now+=ms
        clock=Clock()
        calls=[]
        wifi_calls=[]
        def wifi(*args):
            wifi_calls.append(True)
            if len(wifi_calls)==1: clock.now+=8500
        def get():
            calls.append(clock.now)
            clock.now+=100
            if len(calls)==2: raise ValueError('JSON invalide')
            if len(calls)==4: raise KeyboardInterrupt()
            return (0,0)
        cfg=types.SimpleNamespace(WIFI_SSID='test',WIFI_PASSWORD='test')
        with patch.dict(sys.modules,{'config':cfg}), patch.object(main,'time',clock), \
             patch.object(main,'connect_wifi',wifi), patch.object(main,'get_iss_position',get), \
             patch.object(main,'init_display',return_value=Screen()):
            with self.assertRaises(KeyboardInterrupt): main.main()
        self.assertEqual(len(calls),4)
        self.assertTrue(all(b-a>=3000 for a,b in zip(calls,calls[1:])),calls)
    def test_wifi_failure_skips_get_and_recovers(self):
        class Clock:
            now=0
            def ticks_ms(self): return self.now
            def ticks_diff(self,a,b): return a-b
            def sleep_ms(self,ms): self.now+=ms
        attempts=[]
        calls=[]
        def wifi(*args):
            attempts.append(True)
            if len(attempts)==1: raise OSError('Wi-Fi coupe')
        def get():
            calls.append(True)
            raise KeyboardInterrupt()
        cfg=types.SimpleNamespace(WIFI_SSID='test',WIFI_PASSWORD='test')
        with patch.dict(sys.modules,{'config':cfg}), patch.object(main,'time',Clock()), \
             patch.object(main,'connect_wifi',wifi), patch.object(main,'get_iss_position',get), \
             patch.object(main,'init_display',return_value=Screen()):
            with self.assertRaises(KeyboardInterrupt): main.main()
        self.assertEqual((len(attempts),len(calls)),(2,1))


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    if not result.wasSuccessful(): sys.exit(1)
