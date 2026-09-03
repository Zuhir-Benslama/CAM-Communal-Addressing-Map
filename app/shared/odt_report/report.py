"""Public high-level statistical report construction."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from .builder import OdtBuilder
from .labels import tr


def build_statistical_report(data: dict[str, Any], output: Path) -> bytes:
    """Build the localised, styled statistical report ODT from *data*."""
    locale = data.get('locale', 'ar')
    b = OdtBuilder(locale)

    title = data.get('title') or tr('title', locale)
    b.title(title)
    b.blank('Spacer')
    b.info_line(tr('date', locale), data.get('date', ''))
    b.info_line(tr('wilaya', locale), data.get('wilaya', ''))
    b.info_line(tr('commune', locale), data.get('commune', ''))

    b.section(tr('general_stats', locale))
    b.table(
        [tr('item', locale), tr('count', locale)],
        [
            [tr('zones', locale), data.get('zones', 0)],
            [tr('roads', locale), data.get('roads', 0)],
            [tr('subdivisions', locale), data.get('subs', 0)],
            [tr('facilities', locale), data.get('orgs', 0)],
            [tr('numberings_total', locale), data.get('num_total', 0)],
            [tr('panels_total', locale), data.get('pan_total', 0)],
        ],
        'Gross',
    )

    b.section(tr('numbering_by_state', locale))
    b.table(
        [tr('status', locale), tr('count', locale)],
        [
            [tr('planneds', locale), data.get('prog', 0)],
            [tr('matched', locale), data.get('right', 0)],
            [tr('mismatched', locale), data.get('wrong', 0)],
            [tr('reserved', locale), data.get('booked', 0)],
            [tr('total', locale), data.get('num_total', 0)],
        ],
        'Num',
    )

    b.section(tr('panels_by_ref', locale))
    b.table(
        [
            tr('status', locale),
            tr('subdivisions', locale),
            tr('facilities', locale),
            tr('roads', locale),
        ],
        [
            [
                tr('planned', locale),
                data.get('pan_city1', 0),
                data.get('pan_org1', 0),
                data.get('pan_road1', 0),
            ],
            [
                tr('mounted', locale),
                data.get('pan_city0', 0),
                data.get('pan_org0', 0),
                data.get('pan_road0', 0),
            ],
            [
                tr('to_move', locale),
                data.get('pan_city2', 0),
                data.get('pan_org2', 0),
                data.get('pan_road2', 0),
            ],
            [
                tr('to_fix', locale),
                data.get('pan_city3', 0),
                data.get('pan_org3', 0),
                data.get('pan_road3', 0),
            ],
        ],
        'Pan',
    )

    b.section(tr('std_panels', locale))
    b.info_line(tr('total', locale), data.get('pan_std', 0))

    created = data.get('creation_date', str(date.today()))
    b.blank('Spacer')
    b.footnote(f'{tr("generated_on", locale)} {created}')
    return b.render(created, output)
