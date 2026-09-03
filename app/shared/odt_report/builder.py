"""In-memory ODF text document builder via lxml."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from lxml import etree

from .meta import meta_xml
from .namespaces import NSMAP, OFFICE, STYLE, TABLE, TEXT, q
from .package import zip_bytes
from .styles import styles_xml


class OdtBuilder:
    """Builds a flat ODF text document via lxml."""

    def __init__(self, locale: str = 'ar') -> None:
        self.locale = locale
        self.content = etree.Element(q('document-content', OFFICE), nsmap=NSMAP)
        self.content.set(q('version', OFFICE), '1.2')
        body = etree.SubElement(self.content, q('body', OFFICE))
        self.text = etree.SubElement(body, q('text', TEXT))

    # -- text helpers -------------------------------------------

    def _paragraph(self, parent: Any, style: str | None = None) -> Any:
        p = etree.SubElement(parent, q('p', TEXT))
        if style:
            p.set(q('style-name', TEXT), style)
        return p

    def _span(self, parent: Any, style: str, value: object) -> None:
        span = etree.SubElement(parent, q('span', TEXT))
        span.set(q('style-name', TEXT), style)
        span.text = str(value)

    # -- public builders ----------------------------------------

    def title(self, value: str) -> None:
        p = self._paragraph(self.text, 'TitleRow')
        self._span(p, 'TitleText', value)

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

        tbl = etree.SubElement(self.text, q('table', TABLE))
        tbl.set(q('name', TABLE), name)
        tbl.set(q('style-name', TABLE), 'Table1')

        for i in range(col_count):
            col = etree.SubElement(tbl, q('table-column', TABLE))
            col.set(q('style-name', TABLE), f'col{i + 1}')

        hdr = etree.SubElement(tbl, q('table-row', TABLE))
        hdr.set(q('style-name', STYLE), 'TableHeaderRow')
        for h in headers:
            cell = etree.SubElement(hdr, q('table-cell', TABLE))
            cell.set(q('style-name', STYLE), 'TableHeaderCell')
            self._paragraph(cell, 'TableHeaderPar').text = str(h)

        for i, row in enumerate(rows, start=1):
            row_el = etree.SubElement(tbl, q('table-row', TABLE))
            row_el.set(q('style-name', STYLE), 'TableBodyRow')
            cell_style = 'TableBodyCellZebra' if i % 2 == 0 else 'TableCell'
            for value in row:
                cell = etree.SubElement(row_el, q('table-cell', TABLE))
                cell.set(q('style-name', STYLE), cell_style)
                p = self._paragraph(cell, 'BodyText')
                p.set(q('style-name', TEXT), 'CellText')
                p.text = str(value)

    def render(self, created: str, output: Path) -> bytes:
        content_xml = etree.tostring(
            self.content, xml_declaration=True, encoding='UTF-8', pretty_print=True
        )
        return zip_bytes(content_xml, styles_xml(), meta_xml(created), output)
