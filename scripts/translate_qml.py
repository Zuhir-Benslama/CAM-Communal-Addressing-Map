"""Translate Arabic display labels to English in QML style files.
Changes `name` (ValueMap) and `label` (category) attributes.
Keeps `value` attributes unchanged (these are database primary keys).
"""
import os
import re
import json

QML_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'style', 'default'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'style', 'customized'),
]
TEMPLATE_DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template_data')


def load_json_translations():
    """Build Arabic->English map from existing JSON template data."""
    t = {}
    files = ['type_voie.json', 'type_zone.json', 'type_cite.json',
             'situation_Montage.json', 'Etat_Numerotation.json']
    for fname in files:
        path = os.path.join(TEMPLATE_DATA, fname)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for entry in data:
                pk = entry.get('pk', '')
                en = entry.get('label_en', '')
                if pk and en:
                    t[pk] = en
    return t


# Road type translations (from type_voie.json label_en)
# Already loaded by load_json_translations()

# Additional road types from customized/road.qml that differ from JSON
ROAD_EXTRA = {
    "آخر": "Other",
}

# Organization type translations (from org.qml ValueMap)
ORG_TYPES = {
    "إقامة جامعية": "University Residence",
    "اخر": "Other",
    "ثانوية": "High School",
    "جامعة": "University",
    "حماية مدنية": "Civil Protection",
    "دار الحضانة": "Kindergarten",
    "دار الشباب": "Youth Center",
    "دار الطفولة": "Children's Home",
    "دار المسنين": "Elderly Home",
    "روضة أطفال": "Nursery School",
    "عيادة متعددة الخدمات": "Polyclinic",
    "قاعة العلاج": "Treatment Room",
    "قاعة حفلات": "Event Hall",
    "قاعة متعددة الرياضات": "Multi-Sports Hall",
    "قصر الرياضة": "Sports Palace",
    "مؤسسة إستشفائية": "Hospital",
    "مؤسسة الصحة الجوارية": "Local Health Institution",
    "متحف": "Museum",
    "متوسطة": "Middle School",
    "محطة": "Station",
    "مخبر بلدي": "Municipal Laboratory",
    "مدرسة": "School",
    "مدرسة قرانية": "Quranic School",
    "مركب رياضي جواري": "Local Sports Complex",
    "مركز بريدي": "Postal Center",
    "مركز تجاري": "Shopping Center",
    "مركز تقافي": "Cultural Center",
    "مركز تكوين": "Training Center",
    "مركز ثقافي": "Cultural Center",
    "مركز صحي": "Health Center",
    "مركز طبي اجتماعي": "Medical-Social Center",
    "مسبح بلدي": "Municipal Pool",
    "مستشفى": "Hospital",
    "مستوصف": "Dispensary",
    "مسجد": "Mosque",
    "مسرح": "Theater",
    "معهد": "Institute",
    "مكتبة بلدية": "Municipal Library",
    "ملحقة بلدية": "Municipal Annex",
    "ملعب": "Stadium",
    "ملعب بلدي": "Municipal Stadium",
    "ملعب جواري": "Local Stadium",
    "نزل الشرطة": "Police Station",
    "وكالة بنكية": "Bank Agency",
    "الدرك الوطني": "National Gendarmerie",
    "حديقة": "Park",
    "سوق": "Market",
    "مقر البلدية": "Municipality Headquarters",
    "مقبرة": "Cemetery",
    "الجزائرية للمياه": "Algerian Water Company",
    "محافظة الغابات": "Forest Directorate",
}

# Organization category translations (from customized/org.qml categorizedSymbol)
ORG_CATEGORIES = {
    "الهيئات و المرافق الصحية": "Health Bodies & Facilities",
    "مرافق النقل و المواصلات": "Transport Facilities",
    "الهيئات و المرافق المالية و السياحية": "Financial & Tourism Bodies",
    "الهيئات و المرافق الدينية": "Religious Bodies & Facilities",
    "الهيئات و المرافق التربوية والجامعية و التكوينية": "Educational & Training Bodies",
    "المرافق الإقامية": "Residential Facilities",
    "الهيئات و المرافق الرياضية و الثقافية": "Sports & Cultural Bodies",
    "الهيئات و المرافق القطاعية": "Sectoral Bodies & Facilities",
    "الهيئات و المرافق الأمنية": "Security Bodies & Facilities",
    "آخر": "Other",
}

# Panel status translations (from customized/pan.qml categorizedSymbol)
PANEL_STATUSES = {
    "لتصحيحها": "To Be Corrected",
    "مبرمجة": "Programmed",
    "مركبة": "Installed",
    "لنقلها": "To Be Moved",
}

# Numbering state translations (from customized/num.qml categorizedSymbol)
NUM_STATES = {
    "مرقمة ومطابقة": "Numbered and Matching",
    "مرقمة وغير مطابقة": "Numbered and Mismatched",
    "محجوز(ة)": "Reserved",
}


def build_translation_map():
    """Build complete Arabic→English translation dictionary."""
    t = {}
    t.update(load_json_translations())
    t.update(ROAD_EXTRA)
    t.update(ORG_TYPES)
    t.update(ORG_CATEGORIES)
    t.update(PANEL_STATUSES)
    t.update(NUM_STATES)
    return t


def translate_qml_file(filepath, trans_map):
    """Translate Arabic display labels in a QML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0
    # Sort by length descending to avoid partial substring matches
    sorted_items = sorted(trans_map.items(), key=lambda x: -len(x[0]))

    for arabic, english in sorted_items:
        # Replace `name="Arabic"` (ValueMap entries) - only when preceded by space
        old_name = f' name="{arabic}"'
        new_name = f' name="{english}"'
        if old_name in content:
            content = content.replace(old_name, new_name)
            changes += content.count(new_name)

        # Replace `label="Arabic"` (category entries)
        old_label = f' label="{arabic}"'
        new_label = f' label="{english}"'
        if old_label in content:
            content = content.replace(old_label, new_label)
            changes += content.count(new_label)

    if changes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ {os.path.basename(filepath)}: {changes} translations applied")
    else:
        print(f"  - {os.path.basename(filepath)}: no changes")
    return changes


def main():
    trans_map = build_translation_map()
    print(f"Loaded {len(trans_map)} translation entries")

    total_changes = 0
    for qml_dir in QML_DIRS:
        if not os.path.isdir(qml_dir):
            continue
        for fname in sorted(os.listdir(qml_dir)):
            if fname.endswith('.qml'):
                fpath = os.path.join(qml_dir, fname)
                total_changes += translate_qml_file(fpath, trans_map)

    print(f"\nTotal translations applied: {total_changes}")


if __name__ == '__main__':
    main()
