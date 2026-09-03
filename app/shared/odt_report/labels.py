"""Localised label catalog for the statistical report."""

from __future__ import annotations

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


def tr(key: str, locale: str) -> str:
    """Return the localised label for *key* in *locale*, falling back to ar."""
    entry = _LABELS.get(key)
    if not entry:
        return key
    return entry.get(locale, entry['ar'])


# Custom colours used by the styles module (kept here for a single home).
ACCENT = '#1f4e79'
ACCENT_LIGHT = '#ddebf7'
ZEBRA = '#f2f7fc'
WHITE = '#ffffff'
CELL_BORDER = '0.5pt solid #7f7f7f'
CELL_PADDING = '0.12cm'
