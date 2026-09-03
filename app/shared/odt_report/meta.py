"""ODF meta.xml member generation."""

from lxml import etree

from .namespaces import META, OFFICE, q


def meta_xml(created: str) -> bytes:
    """Return the ``meta.xml`` member as bytes."""
    root = etree.Element(q('document-meta', OFFICE))
    root.set(q('version', OFFICE), '1.2')
    meta = etree.SubElement(root, q('meta', OFFICE))
    etree.SubElement(meta, q('creation-date', META)).text = created
    etree.SubElement(meta, q('generator', META)).text = 'CAM'
    return etree.tostring(
        root, xml_declaration=True, encoding='UTF-8', pretty_print=True
    )
