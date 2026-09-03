"""ODT zip package assembly."""

from __future__ import annotations

import zipfile
from pathlib import Path

from lxml import etree

from .namespaces import MANIFEST, MIME, q


def _manifest_xml() -> bytes:
    root = etree.Element(q('manifest', MANIFEST))
    root.set(q('version', MANIFEST), '1.2')

    def entry(path: str, media: str) -> None:
        el = etree.SubElement(root, q('file-entry', MANIFEST))
        el.set(q('full-path', MANIFEST), path)
        el.set(q('media-type', MANIFEST), media)

    entry('/', MIME)
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
            MIME.encode('utf-8'),
            compress_type=zipfile.ZIP_STORED,
        )
        zf.writestr('META-INF/manifest.xml', _manifest_xml())
        zf.writestr('content.xml', content_xml)
        zf.writestr('styles.xml', styles)
        zf.writestr('meta.xml', meta)
    return output.read_bytes()
