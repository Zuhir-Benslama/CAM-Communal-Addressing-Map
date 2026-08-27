"""Programmatic ODF (OpenDocument Text) report generation.

Builds a valid ``.odt`` statistical report directly with :mod:`lxml` so the
output is reproducible in CI/builds and does not depend on opaque binary
templates. The report is localised (Arabic / French / English, defaulting to
Arabic for right-to-left layout) and styled with a coloured title band,
shaded section headers, bordered tables with a highlighted header row and
zebra-striped body rows.
"""

from __future__ import annotations

import zipfile
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any

from lxml import etree

OFFICE = 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
TABLE = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
TEXT = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
STYLE = 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'
FO = 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'
META = 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0'
MANIFEST = 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0'

NSMAP = {
    'office': OFFICE,
    'table': TABLE,
    'text': TEXT,
    'style': STYLE,
    'fo': FO,
}

_MIME = 'application/vnd.oasis.opendocument.text'

_ACCENT = '#1f4e79'  # deep blue used for title band and section headers
_ACCENT_LIGHT = '#ddebf7'
_ZEBRA = '#f2f7fc'
_WHITE = '#ffffff'


def _q(tag: str, uri: str) -> str:
    """Return a Clark-notation qualified name for *tag* in namespace *uri*."""
    return f'{{{uri}}}{tag}'


# ---------------------------------------------------------------------------
# Localisation
# ---------------------------------------------------------------------------

_LABELS: dict[str, dict[str, str]] = {
    'title': {
        'ar': 'التقرير الإحصائي',
        'fr': 'Rapport Statistique',
        'en': 'Statistical Report',
    },
    'date': {'ar': 'التاريخ', 'fr': 'Date', 'en': 'Date'},
    'wilaya': {'ar': 'الولاية', 'fr': 'Wilaya', 'en': 'Wilaya'},
    'commune': {'ar': 'البلدية', 'fr': 'Commune', 'en': 'Commune'},
    'general_stats': {
        'ar': 'إحصائيات عامة',
        'fr': 'Statistiques Générales',
        'en': 'General Statistics',
    },
    'item': {'ar': 'العنصر', 'fr': 'Élément', 'en': 'Item'},
    'count': {'ar': 'العدد', 'fr': 'Nombre', 'en': 'Count'},
    'zones': {'ar': 'المناطق', 'fr': 'Zones', 'en': 'Zones'},
    'roads': {'ar': 'الطرق', 'fr': 'Routes', 'en': 'Roads'},
    'subdivisions': {
        'ar': 'التجزئات',
        'fr': 'Lotissements',
        'en': 'Subdivisions',
    },
    'facilities': {
        'ar': 'المرافق',
        'fr': 'Équipements',
        'en': 'Facilities',
    },
    'numberings_total': {
        'ar': 'مجموع المداخل',
        'fr': 'Total des numéros',
        'en': 'Total numberings',
    },
    'panels_total': {
        'ar': 'مجموع اللوحات',
        'fr': 'Total des plaques',
        'en': 'Total panels',
    },
    'numbering_by_state': {
        'ar': 'المداخل حسب الحالة',
        'fr': 'Numéros par état',
        'en': 'Numbering by status',
    },
    'status': {'ar': 'الحالة', 'fr': 'État', 'en': 'Status'},
    'planned': {'ar': 'مبرمجة', 'fr': 'Programmés', 'en': 'Planned'},
    'planneds': {'ar': 'المبرمجة', 'fr': 'Programmés', 'en': 'Planned'},
    'matched': {
        'ar': 'مرقمة ومطابقة',
        'fr': 'Numérotés et conformes',
        'en': 'Numbered & matched',
    },
    'mismatched': {
        'ar': 'مرقمة وغير مطابقة',
        'fr': 'Numérotés non conformes',
        'en': 'Numbered & mismatched',
    },
    'reserved': {'ar': 'المحجوزة', 'fr': 'Réservés', 'en': 'Reserved'},
    'total': {'ar': 'المجموع', 'fr': 'Total', 'en': 'Total'},
    'panels_by_ref': {
        'ar': 'اللوحات حسب المرجع والحالة',
        'fr': 'Plaques par référence et état',
        'en': 'Panels by reference & status',
    },
    'reference': {'ar': 'المرجع', 'fr': 'Référence', 'en': 'Reference'},
    'mounted': {'ar': 'مركبة', 'fr': 'Posées', 'en': 'Mounted'},
    'to_move': {'ar': 'للنقل', 'fr': 'À déplacer', 'en': 'To move'},
    'to_fix': {'ar': 'للتصحيح', 'fr': 'À corriger', 'en': 'To fix'},
    'std_panels': {
        'ar': 'اللوحات بالمقاس المعياري',
        'fr': 'Plaques au format standard',
        'en': 'Panels at standard size',
    },
    'generated_on': {
        'ar': 'أُنشئ في',
        'fr': 'Généré le',
        'en': 'Generated on',
    },
}


def _tr(key: str, locale: str) -> str:
    """Return the localised label for *key* in *locale*, falling back to ar."""
    entry = _LABELS.get(key)
    if not entry:
        return key
    return entry.get(locale, entry['ar'])


# ---------------------------------------------------------------------------
# ODT document builder
# ---------------------------------------------------------------------------


class _OdtBuilder:
    """Builds a flat ODF text document via lxml."""

    def __init__(self, locale: str = 'ar') -> None:
        self.locale = locale
        self.content = etree.Element(_q('document-content', OFFICE), nsmap=NSMAP)
        self.content.set(_q('version', OFFICE), '1.2')
        body = etree.SubElement(self.content, _q('body', OFFICE))
        self.text = etree.SubElement(body, _q('text', TEXT))

    # -- text helpers -------------------------------------------

    def _paragraph(self, parent: Any, style: str | None = None) -> Any:
        p = etree.SubElement(parent, _q('p', TEXT))
        if style:
            p.set(_q('style-name', TEXT), style)
        return p

    def _span(self, parent: Any, style: str, value: object) -> None:
        span = etree.SubElement(parent, _q('span', TEXT))
        span.set(_q('style-name', TEXT), style)
        span.text = str(value)

    # -- public builders ----------------------------------------

    def title(self, value: str) -> None:
        p = self._paragraph(self.text, 'TitleRow')
        self._span(p, 'TitleText', value)

    def subtitle(self, value: str) -> None:
        self._paragraph(self.text, 'Subtitle').text = value

    def blank(self, style: str = 'Spacer') -> None:
        self._paragraph(self.text, style)

    def info_line(self, key: str, value: object) -> None:
        p = self._paragraph(self.text, 'BodyText')
        self._span(p, 'FieldLabel', f'{key}: ')
        self._span(p, 'FieldValue', value)

    def section(self, value: str) -> None:
        p = self._paragraph(self.text, 'SectionHeader')
        self._span(p, 'SectionHeaderText', value)

    def footnote(self, value: str) -> None:
        self._paragraph(self.text, 'FooterText').text = value

    def table(
        self,
        headers: Iterable[str],
        rows: Iterable[Iterable[Any]],
        name: str,
    ) -> None:
        headers = list(headers)
        col_count = len(headers)

        tbl = etree.SubElement(self.text, _q('table', TABLE))
        tbl.set(_q('name', TABLE), name)
        tbl.set(_q('style-name', TABLE), 'Table1')

        for i in range(col_count):
            col = etree.SubElement(tbl, _q('table-column', TABLE))
            col.set(_q('style-name', TABLE), f'col{i + 1}')

        hdr = etree.SubElement(tbl, _q('table-row', TABLE))
        hdr.set(_q('style-name', STYLE), 'TableHeaderRow')
        for h in headers:
            cell = etree.SubElement(hdr, _q('table-cell', TABLE))
            cell.set(_q('style-name', STYLE), 'TableHeaderCell')
            self._paragraph(cell, 'TableHeaderPar').text = str(h)

        for i, row in enumerate(rows, start=1):
            row_el = etree.SubElement(tbl, _q('table-row', TABLE))
            row_el.set(_q('style-name', STYLE), 'TableBodyRow')
            cell_style = 'TableBodyCellZebra' if i % 2 == 0 else 'TableCell'
            for value in row:
                cell = etree.SubElement(row_el, _q('table-cell', TABLE))
                cell.set(_q('style-name', STYLE), cell_style)
                p = self._paragraph(cell, 'BodyText')
                p.set(_q('style-name', TEXT), 'CellText')
                p.text = str(value)

    def render(self, created: str, output: Path) -> bytes:
        content_xml = etree.tostring(
            self.content, xml_declaration=True, encoding='UTF-8', pretty_print=True
        )
        return zip_bytes(content_xml, _styles_xml(), _meta_xml(created), output)


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------


def _text_style(
    el: etree._Element,
    name: str,
    family: str,
    **props: dict[str, str],
) -> None:
    style = etree.SubElement(el, _q('style', STYLE))
    style.set(_q('name', STYLE), name)
    style.set(_q('family', STYLE), family)
    for prop, values in props.items():
        node = etree.SubElement(style, _q(prop, STYLE))
        for attr, val in values.items():
            node.set(_q(attr, FO), val)


def _styles_xml() -> bytes:
    root = etree.Element(_q('document-styles', OFFICE))
    root.set(_q('version', OFFICE), '1.2')
    auto = etree.SubElement(root, _q('automatic-styles', OFFICE))
    styles = etree.SubElement(root, _q('styles', OFFICE))

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
    master = etree.SubElement(styles, _q('master-page', STYLE))
    master.set(_q('name', STYLE), 'Standard')
    master.set(_q('page-layout-name', STYLE), 'PageLayout1')

    # --- paragraph styles ---
    _text_style(
        auto,
        'TitleRow',
        'paragraph',
        **{
            'paragraph-properties': {
                'text-align': 'center',
                'background-color': _ACCENT,
                'margin-top': '0cm',
                'margin-bottom': '0.3cm',
                'padding': '0.25cm',
            }
        },
    )
    _text_style(
        auto,
        'Subtitle',
        'paragraph',
        **{'paragraph-properties': {'text-align': 'center', 'margin-bottom': '0.4cm'}},
    )
    _text_style(
        auto,
        'SectionHeader',
        'paragraph',
        **{
            'paragraph-properties': {
                'text-align': 'right',
                'background-color': _ACCENT_LIGHT,
                'margin-top': '0.5cm',
                'margin-bottom': '0.25cm',
                'padding': '0.15cm',
                'border': f'0.5pt solid {_ACCENT}',
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
                'color': _WHITE,
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
                'color': _WHITE,
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
                'color': _ACCENT,
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
                'border': '0.5pt solid #7f7f7f',
                'padding': '0.12cm',
            }
        },
    )
    _text_style(
        auto,
        'TableBodyCellZebra',
        'table-cell',
        **{
            'table-cell-properties': {
                'border': '0.5pt solid #7f7f7f',
                'padding': '0.12cm',
                'background-color': _ZEBRA,
            }
        },
    )
    _text_style(
        auto,
        'TableHeaderCell',
        'table-cell',
        **{
            'table-cell-properties': {
                'border': '0.5pt solid #1f3864',
                'padding': '0.12cm',
                'background-color': _ACCENT,
            }
        },
    )

    # --- table columns ---
    for col, width in (
        ('col1', '6cm'),
        ('col2', '3cm'),
        ('col3', '3cm'),
        ('col4', '3cm'),
    ):
        col_style = etree.SubElement(auto, _q('style', STYLE))
        col_style.set(_q('name', STYLE), col)
        col_style.set(_q('family', STYLE), 'table-column')
        props = etree.SubElement(col_style, _q('table-column-properties', STYLE))
        props.set(_q('column-width', STYLE), width)

    return etree.tostring(
        root, xml_declaration=True, encoding='UTF-8', pretty_print=True
    )


# ---------------------------------------------------------------------------
# Package assembly
# ---------------------------------------------------------------------------


def _meta_xml(created: str) -> bytes:
    root = etree.Element(_q('document-meta', OFFICE))
    root.set(_q('version', OFFICE), '1.2')
    meta = etree.SubElement(root, _q('meta', OFFICE))
    etree.SubElement(meta, _q('creation-date', META)).text = created
    etree.SubElement(meta, _q('generator', META)).text = 'CAM'
    return etree.tostring(
        root, xml_declaration=True, encoding='UTF-8', pretty_print=True
    )


def _manifest_xml() -> bytes:
    root = etree.Element(_q('manifest', MANIFEST))
    root.set(_q('version', MANIFEST), '1.2')

    def entry(path: str, media: str) -> None:
        el = etree.SubElement(root, _q('file-entry', MANIFEST))
        el.set(_q('full-path', MANIFEST), path)
        el.set(_q('media-type', MANIFEST), media)

    entry('/', _MIME)
    entry('content.xml', 'text/xml')
    entry('styles.xml', 'text/xml')
    entry('meta.xml', 'text/xml')
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8')


def zip_bytes(content_xml: bytes, styles: bytes, meta: bytes, output: Path) -> bytes:
    """Write a valid ODT package to *output* and return its bytes.

    The ``mimetype`` member must be first and stored uncompressed for an
    ODF-compliant reader to accept the package.
    """

    with zipfile.ZipFile(output, 'w') as zf:
        zf.writestr(
            zipfile.ZipInfo('mimetype'),
            _MIME.encode('utf-8'),
            compress_type=zipfile.ZIP_STORED,
        )
        zf.writestr('META-INF/manifest.xml', _manifest_xml())
        zf.writestr('content.xml', content_xml)
        zf.writestr('styles.xml', styles)
        zf.writestr('meta.xml', meta)
    return output.read_bytes()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_statistical_report(data: dict[str, Any], output: Path) -> bytes:
    """Build the localised, styled statistical report ODT from *data*."""
    locale = data.get('locale', 'ar')
    b = _OdtBuilder(locale)

    title = data.get('title') or _tr('title', locale)
    b.title(title)
    b.blank('Spacer')
    b.info_line(_tr('date', locale), data.get('date', ''))
    b.info_line(_tr('wilaya', locale), data.get('wilaya', ''))
    b.info_line(_tr('commune', locale), data.get('commune', ''))

    b.section(_tr('general_stats', locale))
    b.table(
        [_tr('item', locale), _tr('count', locale)],
        [
            [_tr('zones', locale), data.get('zones', 0)],
            [_tr('roads', locale), data.get('roads', 0)],
            [_tr('subdivisions', locale), data.get('subs', 0)],
            [_tr('facilities', locale), data.get('orgs', 0)],
            [_tr('numberings_total', locale), data.get('num_total', 0)],
            [_tr('panels_total', locale), data.get('pan_total', 0)],
        ],
        'Gross',
    )

    b.section(_tr('numbering_by_state', locale))
    b.table(
        [_tr('status', locale), _tr('count', locale)],
        [
            [_tr('planneds', locale), data.get('prog', 0)],
            [_tr('matched', locale), data.get('right', 0)],
            [_tr('mismatched', locale), data.get('wrong', 0)],
            [_tr('reserved', locale), data.get('booked', 0)],
            [_tr('total', locale), data.get('num_total', 0)],
        ],
        'Num',
    )

    b.section(_tr('panels_by_ref', locale))
    b.table(
        [
            _tr('status', locale),
            _tr('subdivisions', locale),
            _tr('facilities', locale),
            _tr('roads', locale),
        ],
        [
            [
                _tr('planned', locale),
                data.get('pan_city1', 0),
                data.get('pan_org1', 0),
                data.get('pan_road1', 0),
            ],
            [
                _tr('mounted', locale),
                data.get('pan_city0', 0),
                data.get('pan_org0', 0),
                data.get('pan_road0', 0),
            ],
            [
                _tr('to_move', locale),
                data.get('pan_city2', 0),
                data.get('pan_org2', 0),
                data.get('pan_road2', 0),
            ],
            [
                _tr('to_fix', locale),
                data.get('pan_city3', 0),
                data.get('pan_org3', 0),
                data.get('pan_road3', 0),
            ],
        ],
        'Pan',
    )

    b.section(_tr('std_panels', locale))
    b.info_line(_tr('total', locale), data.get('pan_std', 0))

    created = data.get('creation_date', str(date.today()))
    b.blank('Spacer')
    b.footnote(f'{_tr("generated_on", locale)} {created}')
    return b.render(created, output)
