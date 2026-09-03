"""ODF XML namespace constants and helpers."""

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

MIME = 'application/vnd.oasis.opendocument.text'


def q(tag: str, uri: str) -> str:
    """Return a Clark-notation qualified name for *tag* in namespace *uri*."""
    return f'{{{uri}}}{tag}'
