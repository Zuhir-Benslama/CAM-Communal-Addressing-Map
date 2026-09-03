"""ODF document style XML generation."""

from __future__ import annotations

from lxml import etree

from .labels import ACCENT, ACCENT_LIGHT, CELL_BORDER, CELL_PADDING, WHITE, ZEBRA
from .namespaces import FO, OFFICE, STYLE, q

_COLUMNS = (('col1', '6cm'), ('col2', '3cm'), ('col3', '3cm'), ('col4', '3cm'))


def _text_style(
    el: etree._Element,
    name: str,
    family: str,
    **props: dict[str, str],
) -> None:
    style = etree.SubElement(el, q('style', STYLE))
    style.set(q('name', STYLE), name)
    style.set(q('family', STYLE), family)
    for prop, values in props.items():
        node = etree.SubElement(style, q(prop, STYLE))
        for attr, val in values.items():
            node.set(q(attr, FO), val)


def styles_xml() -> bytes:
    """Return the ``styles.xml`` member as bytes."""
    root = etree.Element(q('document-styles', OFFICE))
    root.set(q('version', OFFICE), '1.2')
    auto = etree.SubElement(root, q('automatic-styles', OFFICE))
    styles = etree.SubElement(root, q('styles', OFFICE))

    # --- page ---
    _text_style(
        auto,
        'PageLayout1',
        'page-layout',
        **{
            'page-layout-properties': {
                'margin-top': '2cm',
                'margin-bottom': '2cm',
                'margin-left': '2cm',
                'margin-right': '2cm',
            }
        },
    )
    master = etree.SubElement(styles, q('master-page', STYLE))
    master.set(q('name', STYLE), 'Standard')
    master.set(q('page-layout-name', STYLE), 'PageLayout1')

    # --- paragraph styles ---
    _text_style(
        auto,
        'TitleRow',
        'paragraph',
        **{
            'paragraph-properties': {
                'text-align': 'center',
                'background-color': ACCENT,
                'margin-top': '0cm',
                'margin-bottom': '0.3cm',
                'padding': '0.25cm',
            }
        },
    )
    _text_style(
        auto,
        'SectionHeader',
        'paragraph',
        **{
            'paragraph-properties': {
                'text-align': 'right',
                'background-color': ACCENT_LIGHT,
                'margin-top': '0.5cm',
                'margin-bottom': '0.25cm',
                'padding': '0.15cm',
                'border': f'0.5pt solid {ACCENT}',
            }
        },
    )
    _text_style(
        auto,
        'BodyText',
        'paragraph',
        **{'paragraph-properties': {'text-align': 'right', 'font-size': '12pt'}},
    )
    _text_style(
        auto,
        'Spacer',
        'paragraph',
        **{'paragraph-properties': {'margin-bottom': '0.15cm'}},
    )
    _text_style(
        auto,
        'TableHeaderPar',
        'paragraph',
        **{
            'paragraph-properties': {
                'text-align': 'center',
                'font-size': '12pt',
                'font-weight': 'bold',
                'color': WHITE,
            }
        },
    )
    _text_style(
        auto,
        'CellText',
        'paragraph',
        **{'paragraph-properties': {'text-align': 'center', 'font-size': '12pt'}},
    )
    _text_style(
        auto,
        'FooterText',
        'paragraph',
        **{
            'paragraph-properties': {
                'text-align': 'center',
                'margin-top': '0.8cm',
                'font-size': '9pt',
                'color': '#666666',
            }
        },
    )

    # --- character styles ---
    _text_style(
        auto,
        'TitleText',
        'text',
        **{
            'text-properties': {
                'font-size': '20pt',
                'font-weight': 'bold',
                'color': WHITE,
            }
        },
    )
    _text_style(
        auto,
        'FieldLabel',
        'text',
        **{'text-properties': {'font-weight': 'bold'}},
    )
    _text_style(auto, 'FieldValue', 'text')
    _text_style(
        auto,
        'SectionHeaderText',
        'text',
        **{
            'text-properties': {
                'font-size': '14pt',
                'font-weight': 'bold',
                'color': ACCENT,
            }
        },
    )

    # --- table styles ---
    _text_style(auto, 'Table1', 'table')
    _text_style(auto, 'TableHeaderRow', 'table-row')
    _text_style(auto, 'TableBodyRow', 'table-row')
    _text_style(
        auto,
        'TableCell',
        'table-cell',
        **{
            'table-cell-properties': {
                'border': CELL_BORDER,
                'padding': CELL_PADDING,
            }
        },
    )
    _text_style(
        auto,
        'TableBodyCellZebra',
        'table-cell',
        **{
            'table-cell-properties': {
                'border': CELL_BORDER,
                'padding': CELL_PADDING,
                'background-color': ZEBRA,
            }
        },
    )
    _text_style(
        auto,
        'TableHeaderCell',
        'table-cell',
        **{
            'table-cell-properties': {
                'border': f'0.5pt solid {ACCENT}',
                'padding': CELL_PADDING,
                'background-color': ACCENT,
            }
        },
    )

    # --- table columns ---
    for col, width in _COLUMNS:
        col_style = etree.SubElement(auto, q('style', STYLE))
        col_style.set(q('name', STYLE), col)
        col_style.set(q('family', STYLE), 'table-column')
        props = etree.SubElement(col_style, q('table-column-properties', STYLE))
        props.set(q('column-width', STYLE), width)

    return etree.tostring(
        root, xml_declaration=True, encoding='UTF-8', pretty_print=True
    )
