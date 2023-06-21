import os
import logging
from PIL import Image
from raw import export_image_to_raw, load_raw_image

export_in = "/Users/fra/dev/game-amiga-muses/artwork/muse-wip/vues/export-in/"
export_out = "/Users/fra/dev/game-amiga-muses/artwork/muse-wip/vues/export-out/"
export_debug = "/Users/fra/dev/game-amiga-muses/artwork/muse-wip/vues/export-debug/"


def convert_all_png_to_raw(source_dir, dest_dir, debug_dir=None, log_file='conversion.log'):
    # Set up logging
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

    # Check if the destination directory exists, if not, create it
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        logging.info(f"Created destination directory: {dest_dir}")

    # Iterate through all files in the source directory
    for filename in os.listdir(source_dir):
        if filename.endswith(".png"):
            # Load the image using PIL
            img_path = os.path.join(source_dir, filename)
            try:
                image = Image.open(img_path)
            except Exception as e:
                logging.error(f"Error opening image {img_path}: {e}")
                continue

            # Convert the image to RAW format
            raw_filename = filename.replace(".png", ".raw")
            raw_path = os.path.join(dest_dir, raw_filename)
            try:
                debug_image = export_image_to_raw(image, raw_path)
                if debug_dir is not None:
                    debug_path = os.path.join(debug_dir, filename)
                    debug_image.save(debug_path)
                logging.info(f"Successfully converted {img_path} to {raw_path}")

            except Exception as e:
                logging.error(f"Error converting {img_path} to {raw_path}: {e}")

convert_all_png_to_raw(export_in, export_out, export_debug)