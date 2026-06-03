"""Report and map generation using ODT templates."""

# pylint: disable=import-error,wrong-import-position
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime

# Allow running as a standalone script via subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from py3o.template import Template

from app.shared.constants import (
    CHART_SVG,
    MAP_A0_TEMPLATE,
    MAP_A3_TEMPLATE,
    MAP_PNG,
    NORTH_ARROW_SVG,
    SCALE_BAR_SVG,
    SITUATION_PNG,
    SYMBOLS_SVG,
    TEMPLATE_CMD,
    TEMPLATE_REP,
    TMP_JSON,
)

logger = logging.getLogger(__name__)


def _output_path(data_dict: dict, filename: str) -> str:
    """Return the full path for *filename* inside the chosen output dir."""
    out_dir = data_dict.get('output_dir', '.')
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, filename)


def generate_report() -> None:
    """Generate a report ODT from template."""
    template_path = TEMPLATE_REP

    with open(TMP_JSON, encoding='utf-8') as file:
        data_dict = json.load(file)
        t = Template(
            template_path,
            _output_path(
                data_dict,
                f'rapport_{datetime.now().date().strftime("%Y-%m-%d")}.odt',
            ),
        )
        t.render(data_dict)


def generate_order_form() -> None:
    """Generate an order form ODT from template."""
    template_path = TEMPLATE_CMD

    with open(TMP_JSON, encoding='utf-8') as file:
        data_dict = json.load(file)
        t = Template(
            template_path,
            _output_path(
                data_dict,
                f'commande_{datetime.now().date().strftime("%Y-%m-%d")}.odt',
            ),
        )
        t.render(data_dict)


def _find_soffice() -> str:
    """Locate LibreOffice soffice binary: env var SOFFICE_EXE, or PATH."""
    path = os.getenv('SOFFICE_EXE')
    if path:
        if not os.path.isfile(path) or not os.access(path, os.X_OK):
            raise OSError(f'SOFFICE_EXE path is not executable: {path}')
        return path
    path = shutil.which('soffice')
    if path:
        return path
    raise OSError(
        'LibreOffice (soffice) not found. '
        'Set SOFFICE_EXE env var or install LibreOffice.'
    )


def map_a3() -> None:
    """Generate A3 map and convert to PDF."""
    template_path = MAP_A3_TEMPLATE

    with open(TMP_JSON, encoding='utf-8') as file:
        data_dict = json.load(file)
        output_dir = data_dict.get('output_dir', '.')
        num_plan = data_dict.get('num_plan', 'map')

        t = Template(
            template_path,
            _output_path(
                data_dict,
                f'map_{num_plan}.odt',
            ),
        )
        t.set_image_path('staticimage.map', MAP_PNG)
        t.set_image_path('staticimage.north', NORTH_ARROW_SVG)
        t.set_image_path('staticimage.legend', SYMBOLS_SVG)
        t.set_image_path('staticimage.scale', SCALE_BAR_SVG)

        t.render(data_dict)

        soffice_path = _find_soffice()
        input_filename = _output_path(data_dict, f'map_{num_plan}.odt')
        pdf_filename = f'map_{num_plan}.pdf'

        os.makedirs(output_dir, exist_ok=True)

        command = [
            soffice_path,
            '--headless',
            '--convert-to',
            'pdf',
            '--outdir',
            output_dir,
            input_filename,
        ]

        try:
            subprocess.run(command, check=True)
            logger.info(
                'Converted to PDF successfully: %s',
                os.path.join(output_dir, pdf_filename),
            )
            try:
                os.remove(input_filename)
                logger.info('Deleted file: %s', input_filename)
            except FileNotFoundError:
                logger.warning('File not found: %s', input_filename)
            except PermissionError:
                logger.warning(
                    'No permission to delete: %s',
                    input_filename,
                )
            except OSError as e:
                logger.error('Error deleting file: %s', e)
        except subprocess.CalledProcessError as e:
            logger.error('Conversion failed: %s', e)


def map_a4() -> None:
    """Generate A4 map and convert to PDF."""
    template_path = MAP_A0_TEMPLATE

    with open(TMP_JSON, encoding='utf-8') as file:
        data_dict = json.load(file)
        output_dir = data_dict.get('output_dir', '.')
        num_plan = data_dict.get('num_plan', 'map')

        t = Template(
            template_path,
            _output_path(
                data_dict,
                f'map_{num_plan}.odt',
            ),
        )
        t.set_image_path('staticimage.map', MAP_PNG)
        t.set_image_path('staticimage.north', NORTH_ARROW_SVG)
        t.set_image_path('staticimage.legend', SYMBOLS_SVG)
        t.set_image_path('staticimage.scale', SCALE_BAR_SVG)
        t.set_image_path('staticimage.situation', SITUATION_PNG)
        t.set_image_path('staticimage.chart', CHART_SVG)
        t.render(data_dict)
        soffice_path = _find_soffice()

        input_filename = _output_path(data_dict, f'map_{num_plan}.odt')

        command = [
            soffice_path,
            '--headless',
            '--convert-to',
            'pdf',
            '--outdir',
            output_dir,
            input_filename,
        ]

        try:
            subprocess.run(command, check=True)
            logger.info(
                'Converted to PDF successfully: %s',
                os.path.join(output_dir, f'map_{num_plan}.pdf'),
            )
            try:
                os.remove(input_filename)
                logger.info('Deleted file: %s', input_filename)
            except FileNotFoundError:
                logger.warning('File not found: %s', input_filename)
            except PermissionError:
                logger.warning(
                    'No permission to delete: %s',
                    input_filename,
                )
            except OSError as e:
                logger.error('Error deleting file: %s', e)
        except subprocess.CalledProcessError as e:
            logger.error('Conversion failed: %s', e)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--method',
        type=int,
        required=True,
        help='Method number to run',
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
        logger.warning('Method %s not recognized.', args.method)
