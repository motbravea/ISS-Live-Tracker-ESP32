# Tests hors carte (sur ordinateur)

Ces tests se lancent avec **Python 3** et **Pillow**. Ils remplacent les dépendances matérielles de l'ESP32 par des simulations pour vérifier la logique de projection, la validation de l'API, le tracé du marqueur et la gestion d'erreurs.

```bash
python -m pip install Pillow
python verification/tests_hors_carte.py
```

**Dernière vérification : 8 novembre 2026 — 10 tests réussis, 0 échec.**

Le résultat fourni n'est **pas** un test de l'écran OLED physique, de l'ESP32 ou de l'API en direct. Les vérifications matérielles doivent être réalisées séparément.
