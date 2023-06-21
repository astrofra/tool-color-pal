# Spécification du Format de Fichier SAFAR BITMAP (SAFB)

Un fichier SAFB se compose d'une en-tête, d'une section de données de l'image et d'une section de palette de couleurs.

## 1. En-tête

- **Signature (4 bytes)** : "SAFB". C'est une séquence d'identification pour identifier que le fichier est de format SAFB.
- **Largeur de l'image (2 bytes)** : La largeur de l'image en pixels, codée en grand-boutiste.
- **Hauteur de l'image (2 bytes)** : La hauteur de l'image en pixels, codée en grand-boutiste.
- **Taille de la palette (2 bytes)** : Le nombre de couleurs dans la palette de l'image, codée en grand-boutiste.

## 2. Section des Données de l'Image

- **Signature (4 bytes)** : "DATA". C'est une séquence d'identification pour indiquer le début des données de l'image.
- **Données de l'image** : Chaque byte représente deux pixels de l'image. Le byte est formé en prenant l'index de couleur du pixel pair (de gauche à droite) et en le décalant de 4 bits vers la gauche, puis en le combinant avec l'index de couleur du pixel impair par une opération OR binaire.

## 3. Section de la Palette de Couleurs

- **Signature (4 bytes)** : "PAL4". C'est une séquence d'identification pour indiquer le début de la palette de couleurs.
- **Données de la palette** : Chaque couleur est représentée par 2 bytes, codée en grand-boutiste. Chaque couleur est convertie en RGB444 (soit 4 bits pour le rouge, 4 bits pour le vert et 4 bits pour le bleu).
