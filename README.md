# ISS Live Tracker — ESP32 🛰️

Projet d’objets connectés réalisé par **Meryem Belouaar et Khalid Asseffar** : affichage de la position de la Station spatiale internationale (ISS) sur une carte du monde miniature à l’aide d’un **ESP32**, de **MicroPython** et d’un **écran OLED SSD1306 (128 × 64)**.

## Fonctionnalités

- Connexion Wi-Fi depuis l’ESP32.
- Récupération de la latitude et de la longitude de l’ISS via l’API Open Notify.
- Conversion des coordonnées géographiques en pixels pour l’écran.
- Tracé simplifié des continents et affichage d’un marqueur « X » sur la position ISS.
- Actualisation régulière, gestion des erreurs de réseau et affichage des états sur l’OLED.

![Aperçu simulé de l’écran OLED](illustrations/Apercu_OLED_Position_Exemple.png)

## Technologies

**MicroPython · Python · ESP32 · Wi-Fi · API REST/JSON · I²C · OLED SSD1306**

## Structure du projet

- `code/` : programme MicroPython et pilotes nécessaires.
- `illustrations/` : schéma de branchement, organigramme et aperçu de l’écran.
- `verification/` : tests logiciels hors carte.
- `Rapport_TP_ISS_Khalid_Meryem.pdf` : rapport technique.
- `Presentation_TP_ISS_Khalid_Meryem_AMELIOREE.pptx` : présentation.

## Installation sur ESP32

1. Installer MicroPython sur un ESP32 compatible et ouvrir Thonny.
2. Brancher l’écran OLED : **3V3 → VCC, GND → GND, GPIO 21 → SDA, GPIO 22 → SCL** (vérifier la carte avant branchement).
3. Copier `code/config_example.py` en `config.py` et compléter les identifiants Wi-Fi **localement**.
4. Transférer les fichiers Python de `code/` à la racine de l’ESP32, ainsi que `config.py`.
5. Exécuter `main.py` depuis la carte. Pour tester l’écran seul, exécuter `test_oled.py`.

**Sécurité :** ne jamais publier `config.py` ou les identifiants du réseau. Le fichier est exclu par `.gitignore`.

## Vérification

Le dossier contient **10 tests logiciels hors matériel** réussis lors de la préparation. Ils valident notamment la projection cartographique, l’analyse des réponses API et la logique de rafraîchissement. Ils **ne prouvent pas** le bon fonctionnement de l’ESP32, de l’OLED ou du réseau réel ; ces essais restent à réaliser/confirmer sur le matériel.

Pour exécuter les tests sur ordinateur :

```bash
python -m pip install Pillow
python verification/tests_hors_carte.py
```

## Contributions

- **Meryem Belouaar** : affichage OLED, projection des coordonnées, tracé des continents et marqueur ISS.
- **Khalid Asseffar** : configuration, câblage, connexion Wi-Fi, récupération des données API et boucle principale.
- **En équipe** : intégration, vérifications et présentation.

*Projet pédagogique — suivi de l’ISS sur un objet connecté.*
