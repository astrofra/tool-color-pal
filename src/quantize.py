import numpy as np
from sklearn.cluster import KMeans

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

# # Exemple d'utilisation
# colors = [
#     [255, 0, 0], [0, 255, 0], [0, 0, 255],
#     # Ajoutez plus de couleurs RGB (8 bits par composante) ici
# ]

# result = quantize_colors(colors)
# print(result)
