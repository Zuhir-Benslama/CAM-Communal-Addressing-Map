"""Report and map generation using ODT templates."""
import json
import os
from datetime import datetime
import subprocess

from py3o.template import Template

from .constants import (
    TEMPLATE_REP, TEMPLATE_CMD, TMP_JSON, MAP_PNG,
    MAP_A3_TEMPLATE, MAP_A0_TEMPLATE, NORTH_ARROW_SVG, SYMBOLS_SVG,
    SCALE_BAR_SVG, CHART_SVG, SITUATION_PNG
)

import logging
logger = logging.getLogger(__name__)



def generate_report() -> None:
    """Generate a report ODT from template."""
    template_path = TEMPLATE_REP

    with open(TMP_JSON, 'r', encoding='utf-8') as file:
        data_dict = json.load(file)
        t = Template(
            template_path,
            f"rapport_{datetime.now().date().strftime('%Y-%m-%d')}.odt"
        )
        t.render(data_dict)


def generate_order_form() -> None:
    """Generate an order form ODT from template."""
    template_path = TEMPLATE_CMD

    with open(TMP_JSON, 'r', encoding='utf-8') as file:
        data_dict = json.load(file)
        t = Template(
            template_path,
            f"commande_{datetime.now().date().strftime('%Y-%m-%d')}.odt"
        )
        t.render(data_dict)

def map_a3() -> None:
    """Generate A3 map and convert to PDF."""
    template_path = MAP_A3_TEMPLATE


    with open(TMP_JSON, 'r', encoding='utf-8') as file:
        data_dict = json.load(file)
        t = Template(template_path, f"map_{data_dict.get('num_plan',None)}.odt")
        t.set_image_path('staticimage.map', MAP_PNG)
        t.set_image_path('staticimage.north', NORTH_ARROW_SVG)
        t.set_image_path('staticimage.legend', SYMBOLS_SVG)
        t.set_image_path('staticimage.scale', SCALE_BAR_SVG)

        t.render(data_dict)


        soffice_path = os.getenv('SOFFICE_EXE')
        if not soffice_path:
            raise OSError("SOFFICE_EXE environment variable is not set")
        if not os.path.isfile(soffice_path) or not os.access(
            soffice_path, os.X_OK
        ):
            raise OSError(f"SOFFICE_EXE path is not executable: {soffice_path}")

        # Define input and output paths
        num_plan = data_dict.get('num_plan',None)
        input_filename = f"map_{num_plan}.odt"
        output_dir = "./"  # Make sure this exists or create it

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        command = [
            soffice_path,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_filename
        ]

        try:
            subprocess.run(command, check=True)
            logger.info(
                "Converted to PDF successfully: %s",
                os.path.join(output_dir, f'map_{num_plan}.pdf')
            )
            try:
                os.remove(input_filename)
                logger.info("Deleted file: %s", input_filename)
            except FileNotFoundError:
                logger.warning("File not found: %s", input_filename)
            except PermissionError:
                logger.warning("No permission to delete: %s", input_filename)
            except Exception as e:
                logger.error("Error deleting file: %s", e)
        except subprocess.CalledProcessError as e:
            logger.error("Conversion failed: %s", e)



def map_a4() -> None:
    """Generate A4 map and convert to PDF."""
    template_path = MAP_A0_TEMPLATE


    with open(TMP_JSON, 'r', encoding='utf-8') as file:
        data_dict = json.load(file)
        t = Template(template_path, f"map_{data_dict.get('num_plan',None)}.odt")
        t.set_image_path('staticimage.map', MAP_PNG)
        t.set_image_path('staticimage.north', NORTH_ARROW_SVG)
        t.set_image_path('staticimage.legend', SYMBOLS_SVG)
        t.set_image_path('staticimage.scale', SCALE_BAR_SVG)
        t.set_image_path('staticimage.situation', SITUATION_PNG)
        t.set_image_path('staticimage.chart', CHART_SVG)
        t.render(data_dict)
        soffice_path = os.getenv('SOFFICE_EXE')
        if not soffice_path:
            raise OSError("SOFFICE_EXE environment variable is not set")
        if not os.path.isfile(soffice_path) or not os.access(
            soffice_path, os.X_OK
        ):
            raise OSError(f"SOFFICE_EXE path is not executable: {soffice_path}")

        # Define input and output paths
        num_plan = data_dict.get('num_plan',None)
        input_filename = f"map_{num_plan}.odt"
        output_dir = "./"

        command = [
            soffice_path,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            input_filename
        ]

        try:
            subprocess.run(command, check=True)
            logger.info(
                "Converted to PDF successfully: %s",
                os.path.join(output_dir, f'map_{num_plan}.pdf')
            )
            try:
                os.remove(input_filename)
                logger.info("Deleted file: %s", input_filename)
            except FileNotFoundError:
                logger.warning("File not found: %s", input_filename)
            except PermissionError:
                logger.warning("No permission to delete: %s", input_filename)
            except Exception as e:
                logger.error("Error deleting file: %s", e)
        except subprocess.CalledProcessError as e:
            logger.error("Conversion failed: %s", e)




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--method', type=int, required=True, help='Method number to run'
    )

    args = parser.parse_args()

    if args.method == 1:
        generate_order_form()
    elif args.method == 2:
        generate_report()
    elif args.method == 3:
        map_a3()
    elif args.method == 4:
        map_a4()
    else:
        logger.warning("Method %s not recognized.", args.method)
