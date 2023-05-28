import numpy as np
from operator import itemgetter
from collections import defaultdict
from sklearn.cluster import KMeans
from collections import Counter
from PIL import Image


def progress_callback_stub(v,a,b,c,d):
    pass

def remap(value, a, b, c, d):
    ratio = (d - c) / (b - a)
    return c + (value - a) * ratio


def sort_palette_by_luminance(palette):
    def luminance(color):
        r, g, b = color
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    return sorted(palette, key=luminance)


def build_color_list_from_image(img, progress_callback=progress_callback_stub, pb_min=0, pb_max=100):
    if img is not None:
        colors = []
        for y in range(img.height):
            progress_callback(remap(y / img.height, 0.0, 1.0, pb_min, pb_max))
            for x in range(img.width):
                color = img.getpixel((x, y))
                # r = (color[0] // 16) * 16
                # g = (color[1] // 16) * 16
                # b = (color[2] // 16) * 16
                # if not([r, g, b] in colors):
                #     colors.append([r, g, b])
                colors.append([color[0], color[1], color[2]])

        print("True Color Palette: " + str(len(colors)) + " colors found.")
        return colors


# def pre_dither_image(img, luma_amplitude=0.05, progress_callback=progress_callback_stub, pb_min=0, pb_max=100):
#     img_data = np.array(img)
#     h, w, _ = img_data.shape

#     for y in range(h):
#         progress_callback(remap(y / h, 0.0, 1.0, pb_min, pb_max))
#         for x in range(w):
#             if (x + y) % 2 == 0:
#                 img_data[y, x] = np.clip(img_data[y, x] * (1.0 - luma_amplitude), 0, 255)
#             else:
#                 img_data[y, x] = np.clip(img_data[y, x] * (1.0 + luma_amplitude), 0, 255)

#     return Image.fromarray(img_data.astype('uint8'))


def overlay_formula(a, b):
    return np.where(a <= 0.5, 2 * a * b, 1 - 2 * (1 - a) * (1 - b))


def apply_dither_overlay(img, luma_amplitude=0.05, progress_callback=progress_callback_stub, pb_min=0, pb_max=100):
    img_rgb = img.convert("RGB")  # Convertir l'image en RGB
    img_data = np.array(img_rgb, dtype=np.float32) / 255
    h, w, _ = img_data.shape

    overlay_color_even = np.array([(1.0 - luma_amplitude) / 2.0] * 3, dtype=np.float32)
    overlay_color_odd = np.array([(1.0 + luma_amplitude) / 2.0] * 3, dtype=np.float32)

    for y in range(h):
        progress_callback(remap(y / h, 0.0, 1.0, pb_min, pb_max))
        for x in range(w):
            if (x + y) % 2 == 0:
                img_data[y, x] = overlay_formula(img_data[y, x], overlay_color_even)
            else:
                img_data[y, x] = overlay_formula(img_data[y, x], overlay_color_odd)

    return Image.fromarray(np.uint8(img_data * 255))


def quantize_colors(colors, n_colors=16, method="kmeans"):
    if method.lower() == "kmeans":
        return quantize_colors_kmeans(colors, n_colors)
    if method.lower() == "median cut":
        return quantize_colors_median_cut(colors, n_colors)
    if method.lower() == "popularity":
        return quantize_colors_popularity(colors, n_colors)


from collections import Counter

def quantize_colors_popularity(colors, n_colors=16):
    # Normalize the colors
    colors = np.array(colors, dtype=np.int32)

    # We'll count the colors using a Counter, then select the most common ones
    counter = Counter(map(tuple, colors))

    # Initialize the list of representative colors
    representative_colors = []

    # Same loop as before, to handle possible color duplication due to quantization
    requested_colors = n_colors
    while len(representative_colors) < n_colors:
        # Select the most common colors
        representative_colors = [color for color, _ in counter.most_common(requested_colors)]

        # Apply the same quantization
        representative_colors = np.round(np.array(representative_colors) / 17) * 17
        representative_colors = representative_colors.astype(int)

        # Remove duplicates
        representative_colors = np.unique(representative_colors, axis=0)
        representative_colors = representative_colors.tolist()

        requested_colors += 1

    return representative_colors


def quantize_colors_median_cut(colors, n_colors=16):
    # Normalize the colors
    colors = np.array(colors, dtype=np.int32)

    # Let's start with the amount of colors that the user wants
    representative_colors = []

    # Initialize color_buckets with all colors in one bucket
    color_buckets = [colors.tolist()]

    # Same loop as before, to handle possible color duplication due to quantization
    while len(representative_colors) < n_colors:
        print("len(representative_colors) = " + str(len(representative_colors)))

        # Find the longest color dimension in the bucket
        longest_dim = max(range(3), key=lambda dim: max(colors[:,dim]) - min(colors[:,dim]))

        # Select the bucket to split
        # In this case, we choose the bucket with the most colors
        largest_bucket_index = max(range(len(color_buckets)), key=lambda index: len(color_buckets[index]))
        largest_bucket = color_buckets[largest_bucket_index]

        # Sort the selected bucket along the longest dimension
        largest_bucket.sort(key=itemgetter(longest_dim))

        # Find the median color along the longest dimension
        median_index = len(largest_bucket) // 2

        # Split the bucket into two around the median color
        color_buckets[largest_bucket_index] = largest_bucket[:median_index]
        color_buckets.append(largest_bucket[median_index:])

        # At this point, we have the desired number of color buckets
        # We will now find the representative color for each bucket
        # The representative color will be the average color in the bucket
        representative_colors = [np.mean(bucket, axis=0) for bucket in color_buckets]

        # Apply the same quantization
        representative_colors = np.round(np.array(representative_colors) / 17) * 17
        representative_colors = representative_colors.astype(int)

        # Remove duplicates
        representative_colors = np.unique(representative_colors, axis=0)
        representative_colors = representative_colors.tolist()

    return representative_colors



def quantize_colors_kmeans(colors, n_colors=16):
    # Normalize the colors
    colors = np.array(colors, dtype=np.float64) / 255

    # Let's start with the amount of colors that the user wants
    requested_colors = n_colors
    representative_colors = []

    # Because of the quantization (RGB888 -> RGB444)
    # some colors might be duplicated once result of the kmeans
    # was quantized.
    # In this case, we increase the target and start again.
    while len(representative_colors) < n_colors:
        # print("requested_colors = " + str(requested_colors))
        kmeans = KMeans(n_clusters=requested_colors, random_state=42).fit(colors)
        representative_colors = kmeans.cluster_centers_ * 255
        representative_colors = np.round(representative_colors / 17) * 17
        representative_colors = representative_colors
        representative_colors = representative_colors.astype(int)
        representative_colors = np.unique(representative_colors, axis=0)
        representative_colors = representative_colors.tolist()

        requested_colors += 1
    
    return representative_colors


def png_24bit_to_indexed(input_img, representative_colors, progress_callback=progress_callback_stub, pb_min=0, pb_max=100):
    img = input_img

    # Extract the data from the image
    img_data = np.array(img)
    colors = img_data.reshape(-1, 3).tolist()

    # Build a dictionnary to map the colors onto the image
    color_to_index = {tuple(color): idx for idx, color in enumerate(representative_colors)}

    # Create an indexed color buffer with the indexed palette
    indexed_img = Image.new("P", img.size)
    indexed_img.putpalette([item for sublist in representative_colors for item in sublist])

    # Fill in the buffer by writting each pixel
    # using the closest color found in the index palette
    for y in range(img_data.shape[0]):
        progress_callback(remap(y / img_data.shape[0], 0.0, 1.0, pb_min, pb_max))
        for x in range(img_data.shape[1]):
            color = tuple(img_data[y, x])
            closest_color = min(representative_colors, key=lambda c: sum((c_i - color_i) ** 2 for c_i, color_i in zip(c, color)))
            indexed_img.putpixel((x, y), color_to_index[tuple(closest_color)])

    # Return the indexed image
    return indexed_img

# # Exemple d'utilisation avec les informations de l'image
# width = 320
# height = 200

# image = load_raw_image("image.raw", width, height)
# image.save("image.png")  # Sauvegarder l'image chargée

