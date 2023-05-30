import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def plot_colors(colors):
    # Preparer les données pour le graphique
    R = [color[0] for color in colors]
    G = [color[1] for color in colors]
    B = [color[2] for color in colors]

    # Convertir chaque couleur de format RGB à format pour matplotlib
    color_values = [tuple([c/255 for c in color]) for color in colors]

    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    # Placer chaque couleur dans le graphique comme un point
    ax.scatter(R, G, B, s=100, c=color_values, depthshade=False)

    # Nommer les axes
    ax.set_xlabel('R')
    ax.set_ylabel('G')
    ax.set_zlabel('B')

    plt.show(block=False)

    return plt