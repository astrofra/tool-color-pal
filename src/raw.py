from PIL import Image
import struct


def convert_color_to_rgb444(color):
    r = (color[0] >> 4) & 0xF
    g = (color[1] >> 4) & 0xF
    b = (color[2] >> 4) & 0xF
    return (r << 8) | (g << 4) | b


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

    # debug
    return load_raw_image(filename)
    # return None

# from PIL import Image
def load_raw_image(filename):
    width = height = -1
    palette_size = -1
    palette_data = None
    with open(filename, "rb") as file:
        # check if this is a Safar Bitmap file (SAFB)
        file_header = file.read(4)
        if file_header == b"SAFB":
            bin_width = file.read(2)
            width = struct.unpack('>H', bin_width)[0]
            bin_height = file.read(2)
            height = struct.unpack('>H', bin_height)[0]
            bin_palette_size = file.read(2)
            palette_size = struct.unpack('>H', bin_palette_size)[0]

            # check if the bitmap data block follows
            file_header = file.read(4)
            if file_header == b"DATA":
                color_data = file.read(width * height // 2)

                # check if the palette data block follows
                file_header = file.read(4)
                if file_header == b"PAL4":
                    palette_data = file.read(palette_size * 2) # image_data[width * height // 2:]
                else:
                    return None
            else:
                return None
        else:
            return None

    # process the palette data block
    palette = []
    for i in range(0, len(palette_data), 2):
        rgb444 = int.from_bytes(palette_data[i:i+2], byteorder="big")
        r = ((rgb444 >> 8) & 0xF) << 4
        g = ((rgb444 >> 4) & 0xF) << 4
        b = (rgb444 & 0xF) << 4
        palette.append((r, g, b))

    # create a blank PIL bitmap & palette
    image = Image.new("P", (width, height))
    palette_flat = [value for color in palette for value in color]
    image.putpalette(palette_flat)

    pixels = list(image.getdata())

    # process the bitmap data block (recreate the image)
    for i in range(0, len(color_data)):
        byte = color_data[i]
        even_index = (byte >> 4) & 0xF
        odd_index = byte & 0xF
        pixels[i * 2] = even_index
        pixels[i * 2 + 1] = odd_index
        # pixels[i * 2] = odd_index
        # pixels[i * 2 + 1] = even_index

    image.putdata(pixels)
    return image

# GFA Basic routine (untested)
# PROCEDURE LoadRawImage(filename$, width%, height%)
#     OPEN "I", #1, filename$

#     BGET #1, image_data$, width% * height% / 2
#     BGET #1, palette_data$, width% * height% / 2

#     CLOSE #1

#     DIM palette%(0:width% * height% / 4 - 1, 0:2)
#     FOR i% = 0 TO LEN(palette_data$) - 2 STEP 2
#         rgb444% = MKI$(MID$(palette_data$, i% + 1, 2))
#         palette%(i% / 2, 0) = (rgb444% DIV 4096 AND 15) * 16
#         palette%(i% / 2, 1) = (rgb444% DIV 256 AND 15) * 16
#         palette%(i% / 2, 2) = (rgb444% MOD 256 AND 15) * 16
#     NEXT i%

#     DIM pixels%(0:width% * height% - 1)
#     FOR i% = 0 TO LEN(image_data$) - 1
#         byte% = ASC(MID$(image_data$, i% + 1, 1))
#         pixels%(i% * 2) = byte% DIV 16 AND 15
#         pixels%(i% * 2 + 1) = byte% MOD 16
#     NEXT i%

#     ' Modify the following according to how you intend to display or handle the image
#     ' Example: CALL DisplayImage(pixels%, palette%, width%, height%)
# ENDPROC
