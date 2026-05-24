"""Add English fields to JSON template data files.

1. type_organisme.json: Add TypeEn field (from TypeFr French→English)
2. activity.json: Add cat_en and type_en fields
"""
import json
import os
import re

TEMPLATE_DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template_data')

# French→English translation for TypeFr values in type_organisme.json
TYPE_ORG_EN = {
    "Etablissement Hospitalier et Universitaire": "University Hospital",
    "Etablissement Hospitalier": "Hospital",
    "Etablissement Public Hospitalier": "Public Hospital",
    "Etablissement Public de Santé de Proximité": "Local Public Health Institution",
    "Etablissement Hospitalier Spécialisés": "Specialized Hospital",
    "Centre Hospitalo-Universitaire": "University Hospital Center",
    "Centre médical social": "Medical-Social Center",
    "Centre de santé": "Health Center",
    "Clinique": "Clinic",
    "Dispensaire": "Dispensary",
    "Hopital": "Hospital",
    "Polyclinique": "Polyclinic",
    "Salle de soin": "Treatment Room",
    "Unité dépistage Scolaire": "School Screening Unit",
    "Gare": "Station",
    "Port": "Port",
    "Aéroport": "Airport",
    "Bureau de poste": "Post Office",
    "Centre commercial": "Shopping Center",
    "Agence bancaire": "Bank Agency",
    "Centre des chèques postaux": "Postal Check Center",
    "Centre postal": "Postal Center",
    "Hotel": "Hotel",
    "Salle des fetes": "Event Hall",
    "Mosquée": "Mosque",
    "Cimetière": "Cemetery",
    "Ecole Primaire": "Primary School",
    "Collège d\"Enseignement Moyen": "Middle School",
    "Lycée": "High School",
    "Crèche": "Kindergarten",
    "Faculté": "Faculty",
    "Université": "University",
    "Institut": "Institute",
    "Résidance universitaire": "University Residence",
    "Laboratoire de recherche": "Research Laboratory",
    "Maison d'enfance": "Children's Home",
    "Centre de formation": "Training Center",
    "Complexe": "Complex",
    "Résidence": "Residence",
    "Coopérative": "Cooperative",
    "Complexe sportif": "Sports Complex",
    "Complexe sportif de proximité": "Local Sports Complex",
    "Maison de jeunes": "Youth Center",
    "Piscine": "Swimming Pool",
    "Salle omnisports": "Multi-Sports Hall",
    "Stade": "Stadium",
    "Stade de proximité": "Local Stadium",
    "Centre culturel": "Cultural Center",
    "Bibliothèque municipale": "Municipal Library",
    "Musée": "Museum",
    "Théatre": "Theater",
    "Annexe municipale": "Municipal Annex",
    "Direction des impots": "Tax Directorate",
    "Commissariat": "Police Station",
    "Brigade de la gendermerie nationale": "National Gendarmerie",
    "Protection civile": "Civil Protection",
    "Maison de la culture": "Cultural Center",
}

# Category translations
CATEGORY_EN = {
    "الهيئات و المرافق الصحية": "Health Bodies & Facilities",
    "مرافق النقل و المواصلات": "Transport Facilities",
    "الهيئات و المرافق المالية و السياحية": "Financial & Tourism Bodies",
    "الهيئات و المرافق الدينية": "Religious Bodies & Facilities",
    "الهيئات و المرافق التربوية والجامعية و التكوينية": "Educational & Training Bodies",
    "المرافق الإقامية": "Residential Facilities",
    "الهيئات و المرافق الرياضية و الثقافية": "Sports & Cultural Bodies",
    "الهيئات و المرافق القطاعية": "Sectoral Bodies & Facilities",
    "الهيئات و المرافق الأمنية": "Security Bodies & Facilities",
}


def update_type_organisme():
    path = os.path.join(TEMPLATE_DATA, 'type_organisme.json')
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changes = 0
    for entry in data:
        type_fr = entry.get('TypeFr', '')
        cat = entry.get('categorie', '')
        if type_fr and 'TypeEn' not in entry:
            entry['TypeEn'] = TYPE_ORG_EN.get(type_fr, type_fr)
            changes += 1
        if cat and 'categorie_en' not in entry:
            entry['categorie_en'] = CATEGORY_EN.get(cat, cat)
            changes += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"type_organisme.json: {changes} fields added to {len(data)} entries")
    return changes


def update_activity():
    path = os.path.join(TEMPLATE_DATA, 'activity.json')
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Collect unique sectors and types
    sectors = {}
    types = {}
    for entry in data:
        sec = entry.get('القطاع', '')
        typ = entry.get('النوع', '')
        if sec and sec not in sectors:
            sectors[sec] = _translate_sector(sec)
        if typ and typ not in types:
            types[typ] = _translate_activity_type(typ)

    changes = 0
    for entry in data:
        sec = entry.get('القطاع', '')
        typ = entry.get('النوع', '')
        if sec and 'cat_en' not in entry:
            entry['cat_en'] = sectors.get(sec, sec)
            changes += 1
        if typ and 'type_en' not in entry:
            entry['type_en'] = types.get(typ, typ)
            changes += 1

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"activity.json: {changes} fields added to {len(data)} entries")
    return len(sectors), len(types)


def _translate_sector(arabic):
    """Translate activity sector names from Arabic to English."""
    mapping = {
        "إعلام وإتصال": "Media & Communication",
        "بريد و مواصلات": "Post & Telecommunications",
        "تجارة": "Trade",
        "تربية و تعليم": "Education",
        "تسيير": "Management",
        "ثقافة": "Culture",
        "خدمات": "Services",
        "رياضة": "Sports",
        "سياحة": "Tourism",
        "شؤون دينية": "Religious Affairs",
        "صناعة": "Industry",
        "طاقة و مناجم": "Energy & Mines",
        "صحة": "Health",
        "صناعة تقليدية": "Handicrafts",
        "عدل": "Justice",
        "فلاحة": "Agriculture",
        "أمن": "Security",
        "أشغال عمومية و ري": "Public Works & Irrigation",
        "مالية و بنوك": "Finance & Banking",
    }
    return mapping.get(arabic, arabic)


def _translate_activity_type(arabic):
    """Translate activity type names from Arabic to English."""
    mapping = {
        "محطة إذاعة": "Radio Station",
        "محطة بث": "Broadcast Station",
        "محطة تلفزة": "Television Station",
        "مقر جريدة": "Newspaper Office",
        "شركة إتصالات": "Telecommunications Company",
        "وكالة إتصالات": "Communications Agency",
        "وكالة بريدية": "Postal Agency",
        "مكتب بريدي": "Post Office",
        "متجر": "Shop",
        "محل تجاري": "Commercial Store",
        "مخزن": "Warehouse",
        "ورشة": "Workshop",
        "مقهى": "Coffee Shop",
        "مطعم": "Restaurant",
        "مركز تسوق": "Shopping Center",
        "سوق": "Market",
        "مخبزة": "Bakery",
        "مكتبة": "Bookstore",
        "روضة أطفال": "Kindergarten",
        "مدرسة إبتدائية": "Primary School",
        "إكمالية التعليم المتوسط": "Middle School",
        "ثانوية": "High School",
        "جامعة": "University",
        "كلية": "Faculty",
        "معهد": "Institute",
        "مركز التكوين": "Training Center",
        "قاعة العلاج": "Treatment Room",
        "عيادة": "Clinic",
        "عيادة متعددة الخدمات": "Polyclinic",
        "مستشفى": "Hospital",
        "مستوصف": "Dispensary",
        "مخبر تحليل": "Analysis Laboratory",
        "صيدلية": "Pharmacy",
        "مكتب": "Office",
        "وكالة": "Agency",
        "شركة": "Company",
        "مؤسسة": "Institution",
        "بنك": "Bank",
        "وكالة بنكية": "Bank Agency",
        "مكتب صرافة": "Exchange Office",
        "مكتب بريد": "Post Office",
        "فندق": "Hotel",
        "مطعم سياحي": "Tourist Restaurant",
        "وكالة سياحة وأسفار": "Travel Agency",
        "مسبح": "Swimming Pool",
        "ملعب": "Stadium",
        "قاعة رياضة": "Sports Hall",
        "مركز رياضي": "Sports Center",
        "مسجد": "Mosque",
        "مصلى": "Prayer Room",
        "زاوية": "Zawiya",
        "مكتبة مسجد": "Mosque Library",
        "مقبرة": "Cemetery",
        "مركز ثقافي": "Cultural Center",
        "متحف": "Museum",
        "مسرح": "Theater",
        "دار الثقافة": "Cultural Center",
        "قاعة سينما": "Cinema",
        "قاعة حفلات": "Event Hall",
        "مركز ترفيه": "Entertainment Center",
        "مصنع": "Factory",
        "معمل": "Laboratory",
        "وحدة إنتاج": "Production Unit",
        "شركة صناعية": "Industrial Company",
        "ورشة صناعية": "Industrial Workshop",
        "محطة كهرباء": "Power Station",
        "محطة تحويل": "Transformer Station",
        "مكتب طاقة": "Energy Office",
        "محطة نفط": "Oil Station",
        "محطة غاز": "Gas Station",
        "مكتب مناجم": "Mines Office",
        "دار العدالة": "Courthouse",
        "مجلس قضاء": "Judicial Council",
        "نيابة": "Prosecutor's Office",
        "محكمة": "Court",
        "أمن حضري": "Urban Security",
        "أمن ولاية": "Provincial Security",
        "فرقة درك": "Gendarmerie Unit",
        "مزرعة": "Farm",
        "حقل": "Field",
        "مشروع فلاحي": "Agricultural Project",
        "مؤسسة فلاحية": "Agricultural Institution",
        "مقهى": "Cafe",
        "مطعم": "Restaurant",
        "مديرية": "Directorate",
        "مصلحة": "Department",
        "ديوان": "Office",
        "مركز": "Center",
        "محطة خدمات": "Service Station",
        "وكالة عقارية": "Real Estate Agency",
        "مكتب دراسات": "Study Office",
        "مكتب هندسة": "Engineering Office",
    }
    return mapping.get(arabic, arabic)


def main():
    update_type_organisme()
    update_activity()


if __name__ == '__main__':
    main()
