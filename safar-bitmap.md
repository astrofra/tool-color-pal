# Spécification du Format de Fichier SAFAR BITMAP (SAFB)

Un fichier SAFB se compose d'une en-tête, d'une section de données de l'image et d'une section de palette de couleurs.
Les dimensions sont libres, l'image ne fait pas necessairement 320x200 pixels.

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

# Exemples de lecture/écriture

## Python

```python
def export_image_to_raw(image, filename):
    width, height = image.size

    # export image
    with open(filename, "wb") as file:
        pixels = image.load()

        # image width, height, palette size
        file.write(b"SAFB") # 4 bytes for the SAFB (Safar Bitmap) header
        file.write(width.to_bytes(2, byteorder="big")) # 2 bytes for the image width (in pixels)
        file.write(height.to_bytes(2, byteorder="big")) # 2 bytes for the image height (in pixels)
        file.write(len(image.palette.colors).to_bytes(2, byteorder="big")) # 2 bytes for the palette size

        # image data
        file.write(b"DATA") # 4 bytes for the data header
        for row in range(height):
            for col in range(width // 2):
                even_index = pixels[col * 2, row]
                odd_index = pixels[col * 2 + 1, row]
                byte = (even_index << 4) | odd_index
                file.write(byte.to_bytes(1, byteorder="big")) # 2 pixels per byte

        # palette
        file.write(b"PAL4") # 4 bytes for the palette header
        for color in image.palette.colors:
            rgb444 = convert_color_to_rgb444(color)
            file.write(rgb444.to_bytes(2, byteorder="big")) # 2 bytes per color
```

## GFA Basic

Pseudo code, non testé.

```delphi
GFA Basic routine (untested)
PROCEDURE LoadRawImage(filename$, width%, height%)
    OPEN "I", #1, filename$
    BGET #1, image_data$, width% * height% / 2
    BGET #1, palette_data$, width% * height% / 2
    CLOSE #1
    DIM palette%(0:width% * height% / 4 - 1, 0:2)
    FOR i% = 0 TO LEN(palette_data$) - 2 STEP 2
        rgb444% = MKI$(MID$(palette_data$, i% + 1, 2))
        palette%(i% / 2, 0) = (rgb444% DIV 4096 AND 15) * 16
        palette%(i% / 2, 1) = (rgb444% DIV 256 AND 15) * 16
        palette%(i% / 2, 2) = (rgb444% MOD 256 AND 15) * 16
    NEXT i%
    DIM pixels%(0:width% * height% - 1)
    FOR i% = 0 TO LEN(image_data$) - 1
        byte% = ASC(MID$(image_data$, i% + 1, 1))
        pixels%(i% * 2) = byte% DIV 16 AND 15
        pixels%(i% * 2 + 1) = byte% MOD 16
    NEXT i%
    ' Modify the following according to how you intend to display or handle the image
    ' Example: CALL DisplayImage(pixels%, palette%, width%, height%)
ENDPROC
```
