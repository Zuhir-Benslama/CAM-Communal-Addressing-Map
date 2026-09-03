"""Declarative specs for each popup form page.

Consolidates the object name, save kind, and field rows that previously
lived in six near-identical ``*_page.py`` modules.
"""

from typing import TypedDict

from ..form_specs import (
    CITY_ROWS,
    NUM_ROWS,
    ORG_ROWS,
    PAN_ROWS,
    ROAD_ROWS,
    ZONE_ROWS,
    FieldRow,
)


class _PageSpec(TypedDict):
    object_name: str
    save_kind: str
    rows: list[FieldRow]


PAGE_SPECS: dict[str, _PageSpec] = {
    'zone': {'object_name': 'zonePage', 'save_kind': 'zone', 'rows': ZONE_ROWS},
    'road': {'object_name': 'roadPage', 'save_kind': 'roads', 'rows': ROAD_ROWS},
    'org': {'object_name': 'orgPage', 'save_kind': 'org', 'rows': ORG_ROWS},
    'city': {'object_name': 'cityPage', 'save_kind': 'city', 'rows': CITY_ROWS},
    'num': {'object_name': 'numPage', 'save_kind': 'num', 'rows': NUM_ROWS},
    'pan': {'object_name': 'panPage', 'save_kind': 'pan', 'rows': PAN_ROWS},
}
