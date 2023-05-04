import numpy as np
from sklearn.cluster import KMeans
from PIL import Image


def sort_palette_by_luminance(palette):
    def luminance(color):
        r, g, b = color
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    return sorted(palette, key=luminance)

def build_color_list_from_image(img):
    if img is not None:
        colors = []
        for y in range(img.height):
            for x in range(img.width):
                color = img.getpixel((x, y))
                r = (color[0] // 16) * 16
                g = (color[1] // 16) * 16
                b = (color[2] // 16) * 16
                colors.append([r, g, b])

        print("True Color Palette: " + str(len(colors)) + " colors found.")
        return colors


def pre_dither_image(img, luma_amplitude=0.05):
    img_data = np.array(img)
    h, w, _ = img_data.shape

    for y in range(h):
        for x in range(w):
            if (x + y) % 2 == 0:
                img_data[y, x] = np.clip(img_data[y, x] * (1.0 - luma_amplitude), 0, 255)
            else:
                img_data[y, x] = np.clip(img_data[y, x] * (1.0 + luma_amplitude), 0, 255)

    return Image.fromarray(img_data.astype('uint8'))


def overlay_formula(a, b):
    return np.where(a <= 0.5, 2 * a * b, 1 - 2 * (1 - a) * (1 - b))


def apply_trame_overlay(img, luma_amplitude=0.05):
    img_rgb = img.convert("RGB")  # Convertir l'image en RGB
    img_data = np.array(img_rgb, dtype=np.float32) / 255
    # img_data = np.array(img, dtype=np.float32) / 255
    h, w, _ = img_data.shape

    overlay_color_even = np.array([(1.0 - luma_amplitude) / 2.0] * 3, dtype=np.float32)
    overlay_color_odd = np.array([(1.0 + luma_amplitude) / 2.0] * 3, dtype=np.float32)

    for y in range(h):
        for x in range(w):
            if (x + y) % 2 == 0:
                img_data[y, x] = overlay_formula(img_data[y, x], overlay_color_even)
            else:
                img_data[y, x] = overlay_formula(img_data[y, x], overlay_color_odd)

    return Image.fromarray(np.uint8(img_data * 255))


def quantize_colors(colors, n_colors=16):
    # Convertir les couleurs 8 bits en valeurs de 0 à 1
    colors = np.array(colors, dtype=np.float64) / 255

    # Appliquer l'algorithme de k-means
    kmeans = KMeans(n_clusters=n_colors, random_state=42).fit(colors)

    # Obtenir les couleurs représentatives
    representative_colors = kmeans.cluster_centers_ * 255

    # Convertir les couleurs représentatives en 4 bits par composante
    representative_colors_4bit = np.round(representative_colors / 17) * 17
    representative_colors_4bit = representative_colors_4bit.astype(int)

    return representative_colors_4bit.tolist()


def png_24bit_to_indexed(input_img, representative_colors):
    img = input_img

    # Extraire les données de couleur de l'image
    img_data = np.array(img)
    colors = img_data.reshape(-1, 3).tolist()

    # Quantifier les couleurs
    # representative_colors = quantize_colors(colors, n_colors)

    # Créer un dictionnaire pour mapper les couleurs vers leurs indices
    color_to_index = {tuple(color): idx for idx, color in enumerate(representative_colors)}

    # Créer une image indexée avec la palette de couleurs quantisées
    indexed_img = Image.new("P", img.size)
    indexed_img.putpalette([item for sublist in representative_colors for item in sublist])

    # Remplir l'image indexée avec les indices de couleur appropriés
    for y in range(img_data.shape[0]):
        for x in range(img_data.shape[1]):
            color = tuple(img_data[y, x])
            closest_color = min(representative_colors, key=lambda c: sum((c_i - color_i) ** 2 for c_i, color_i in zip(c, color)))
            indexed_img.putpixel((x, y), color_to_index[tuple(closest_color)])

    # Sauvegarder l'image indexée en tant que nouveau fichier PNG
    return indexed_img