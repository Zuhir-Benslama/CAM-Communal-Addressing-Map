"""Generate RNA_en.ts and RNA_fr.ts with translations for all UI strings."""
import xml.etree.ElementTree as ET

TS_HEADER = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.0" language="{lang}" sourcelanguage="ar">
<context>
    <name>RNADialog</name>"""

TS_FOOTER = """</context>
</TS>
"""

EN: dict[str, str] = {}
FR: dict[str, str] = {}

# --- Short labels / buttons ---
def add(ar, en, fr):
    EN[ar] = en
    FR[ar] = fr

add("حفظ", "Save", "Enregistrer")
add("داكن", "Dark", "Sombre")
add("فاتح", "Light", "Clair")
add(" : اسم", "Name:", "Nom :")
add(" : رقم", "Number:", "Numéro :")
add(" : فئة", "Category:", "Catégorie :")
add(" : نوع", "Type:", "Type :")
add(" : نوع ", "Type:", "Type :")
add(" :حالة", "Status:", "État :")
add("إلغاء", "Cancel", "Annuler")
add("تحديث", "Update", "Mettre à jour")
add(" :  فئة", "Category:", "Catégorie :")
add(" : مكرر", "Duplicate:", "Doublon :")
add("الخروج", "Logout", "Quitter")
add("الدخول", "Login", "Connexion")
add("اللغة:", "Language:", "Langue :")
add("المرفق", "Facility", "Équipement")
add("التاريخ", "Date", "Date")
add("المظهر:", "Theme:", "Thème :")
add("الإعدادات", "Settings", "Paramètres")
add("ابدأ الرسم", "Start Drawing", "Commencer le dessin")
add("حدد الطريق", "Select Road", "Sélectionner la voie")
add("حدد المدخل", "Select Entrance", "Sélectionner l'entrée")
add("حدد المرجع", "Select Reference", "Sélectionner la référence")
add("حدد المرفق", "Select Facility", "Sélectionner l'équipement")
add("رقم المخطط", "Plan Number", "Numéro du plan")
add(" : كلمة السر", "Password:", "Mot de passe :")
add("ارسم الطريق", "Draw Road", "Dessiner la voie")
add("ارسم المدخل", "Draw Entrance", "Dessiner l'entrée")
add("ارسم المرفق", "Draw Facility", "Dessiner l'équipement")
add("حدد التجزئة", "Select Subdivision", "Sélectionner le lotissement")
add("حدد المنطقة", "Select Zone", "Sélectionner la zone")
add("حدد الهندسة", "Select Geometry", "Sélectionner la géométrie")
add("قائمة الطرق", "Road List", "Liste des voies")
add("   منجز من طرف ", "Done by", "Réalisé par")
add("نموذج طلبية", "Order Form", "Bon de commande")
add(" : رقم القرار", "Decision No.:", "N° de décision :")
add(" : نوع الطريق", "Road Type:", "Type de voie :")
add(" : نوع المرجع", "Reference Type:", "Type de référence :")
add("إضافة مستخدم", "Add User", "Ajouter un utilisateur")
add("ارسم التجزئة", "Draw Subdivision", "Dessiner le lotissement")
add("ارسم المنطقة", "Draw Zone", "Dessiner la zone")
add("تحديث الطريق", "Update Road", "Mettre à jour la voie")
add("تحديث المدخل", "Update Entrance", "Mettre à jour l'entrée")
add("تحديث المرفق", "Update Facility", "Mettre à jour l'équipement")
add("تسجيل الدخول", "Sign In", "Se connecter")
add("قياس المسافة", "Measure Distance", "Mesurer la distance")
add(" : حدد الخريطة", "Select Map:", "Sélectionner la carte :")
add(": نوع التجزئة", "Subdivision Type:", "Type de lotissement :")
add(": نوع المنطقة", "Zone Type:", "Type de zone :")
add("إنشاء التقرير", "Generate Report", "Générer le rapport")
add("إنشاء الخريطة", "Generate Map", "Générer la carte")
add("تحديث التجزئة", "Update Subdivision", "Mettre à jour le lotissement")
add("تحديث المنطقة", "Update Zone", "Mettre à jour la zone")
add("قائمة المداخل", "Entrance List", "Liste des entrées")
add("قائمة المرافق", "Facility List", "Liste des équipements")
add("منطقة الدراسة", "Study Area", "Zone d'étude")
add(" : اسم المستخدم", "Username:", "Nom d'utilisateur :")
add(" : حالة التركيب", "Mounting Status:", "État de montage :")
add("قائمة التجزئات", "Subdivisions List", "Liste des lotissements")
add("قائمة اللواحات", "Panels List", "Liste des panneaux")
add("إنشاء خريطة الترقيم", "Generate Numbering Map", "Carte de numérotation")
add("إنشاء خريطة اللوحات", "Generate Panels Map", "Carte des panneaux")
add(" : توافر الشكل الهندسي", "Geometry Status:", "Disponibilité géométrie :")
add("استعادة قاعدة البيانات", "Restore Database", "Restaurer la base de données")
add("النشاط المرافق بالمدخل", "Entrance-related Activity", "Activité liée à l'entrée")
add("النسخ الاحتياطي لقاعدة البيانات", "Database Backup", "Sauvegarde BD")
add("مركز التطبيقات الفضائية  2025 ©", "Space Applications Center 2025 ©", "Centre des Applications Spatiales 2025 ©")
add("إنشاء نسخة احتياطية لقاعدة البيانات", "Create Database Backup", "Créer une sauvegarde BD")
add("يرجى إعادة تشغيل QGIS لتطبيق تغيير اللغة", "Please restart QGIS to apply the language change", "Veuillez redémarrer QGIS pour appliquer le changement de langue")

# --- List / entity dialog labels ---
add("اسم", "Name", "Nom")
add("رقم", "Number", "Numéro")
add("نوع", "Type", "Type")
add("حالة", "Status", "Statut")
add("المفتاح", "ID", "ID")
add("رقم القرار", "Decision No.", "N° décision")
add("الطريق", "Road", "Voie")
add("التجزئة", "Subdivision", "Lotissement")
add("تكرار", "Duplicate", "Doublon")
add("مستخدم", "User", "Utilisateur")
add("الأبعاد", "Dimensions", "Dimensions")
add("نوع المرجع", "Reference Type", "Type référence")
add("الحالة", "Status", "Statut")
add("تسمية", "Label", "Étiquette")
add("بلديتي", "My Municipality", "Ma Municipalité")
add("السابق", "Previous", "Précédent")
add("التالي", "Next", "Suivant")
add("الصفحة", "Page", "Page")
add("  قائمة ", "List of ", "Liste des ")
add("المداخل", "Entrances", "Entrées")
add("اللواحات", "Panels", "Panneaux")
add("بدون نشاط", "No Activity", "Aucune activité")
add("\u202Bورقة A3 للعمل الميداني\u202C", "A3 Paper for Fieldwork", "Papier A3 pour travail terrain")
add("\u202Bورقة A0 للإدارة\u202C", "A0 Paper for Administration", "Papier A0 pour administration")

# --- Database seed data (road types) ---
add("شارع", "Street", "Rue")
add("نهج", "Alley", "Ruelle")
add("زقاق", "Lane", "Impasse")
add("مجاز", "Passage", "Passage")
add("طريق ترابي", "Dirt Road", "Chemin de terre")
add("طريق مسدود", "Dead End", "Impasse")
add("منقطع ممر", "Cut-through", "Passage coupé")
add("درب", "Path", "Sentier")
add("طريق منحدر", "Sloped Road", "Route en pente")
add("منحدر", "Slope", "Pente")
add("مدرج", "Steps", "Escalier")
add("جسر مشاة", "Footbridge", "Passerelle")
add("جسر خاص بالراجلين", "Pedestrian Bridge", "Pont piéton")
add("جادة", "Boulevard", "Boulevard")
add("طريق خاص", "Private Road", "Voie privée")
add("ممر", "Passageway", "Passage")
add("مسار بلدي", "Municipal Path", "Chemin communal")
add("مسار", "Path", "Piste")
add("مسار ولائي", "Provincial Path", "Chemin de wilaya")
add("طريق وطني", "National Road", "Route nationale")

# --- Database seed data (zone types) ---
add("منطقة نشاطات", "Activity Zone", "Zone d'activités")
add("منطقة صناعية", "Industrial Zone", "Zone industrielle")
add("قطب عمراني", "Urban Pole", "Pôle urbain")
add("منطقة", "Zone", "Zone")
add("دوار", "Roundabout", "Rond-point")
add("قرية", "Village", "Village")
add("مشتة", "Hamlet", "Hameau")
add("حي", "Neighborhood", "Quartier")

# --- Database seed data (subdivision types) ---
add("مجمع سكني", "Housing Complex", "Complexe résidentiel")
add("تعاونية", "Cooperative", "Coopérative")
add("مركب", "Compound", "Complexe")
add("تقسيم", "Division", "Division")
add("إقامة", "Residence", "Résidence")
add("مجموعة", "Group", "Groupe")
add("حي سكني", "Residential Neighborhood", "Quartier résidentiel")
add("مجمع عقاري", "Real Estate Complex", "Promotion immobilière")
add("تجزئة", "Subdivision", "Lotissement")

# --- Database seed data (mounting statuses) ---
add("مبرمجة", "Programmed", "Programmé")
add("مركبة", "Installed", "Installé")
add("لتصحيحها", "To Be Corrected", "À corriger")
add("لنقلها", "To Be Moved", "À déplacer")

# --- Database seed data (numbering states) ---
add("مبرمجة", "Programmed", "Programmé")
add("مرقمة ومطابقة", "Numbered and Matching", "Numéroté et conforme")
add("مرقمة وغير مطابقة", "Numbered and Mismatched", "Numéroté et non conforme")
add("محجوز(ة)", "Reserved", "Réservé")

# --- Messages & notifications ---
add("تم تحديث هذا الطريق بنجاح", "Road updated successfully", "Voie mise à jour avec succès")
add("لا يمكن تحديث  الطريق", "Cannot update road", "Impossible de mettre à jour la voie")
add("تم تحديث هذا المرفق بنجاح", "Facility updated successfully", "Équipement mis à jour avec succès")
add("لا يمكن تحديث  المرفق", "Cannot update facility", "Impossible de mettre à jour l'équipement")
add("تم تحديث هذا الحي بنجاح", "Subdivision updated successfully", "Lotissement mis à jour avec succès")
add("لا يمكن تحديث  الحي", "Cannot update subdivision", "Impossible de mettre à jour le lotissement")
add("تم تحديث هذه المنطقة بنجاح", "Zone updated successfully", "Zone mise à jour avec succès")
add("لا يمكن تحديث   المنطقة", "Cannot update zone", "Impossible de mettre à jour la zone")
add("تم تحديث هذه اللوحة بنجاح", "Panel updated successfully", "Panneau mis à jour avec succès")
add("لا يمكن تحديث  اللوحة", "Cannot update panel", "Impossible de mettre à jour le panneau")
add("تم تحديث هذا المدخل بنجاح", "Entrance updated successfully", "Entrée mise à jour avec succès")
add("نوع المرجع غير محدد", "Reference type not selected", "Type de référence non sélectionné")
add("تمة إظافة   نوع الطريق", "Road type added", "Type de voie ajouté")
add("تمة إظافة   نوع المنطقة", "Zone type added", "Type de zone ajouté")
add("تمة إظافة  نوع التجزئة", "Subdivision type added", "Type de lotissement ajouté")
add("تمة إظافة  نوع المرفق", "Facility type added", "Type d'équipement ajouté")
add("تمة إظافة  نوع النشاط", "Activity type added", "Type d'activité ajouté")
add("يتم إظافة  نوع التجزئة", "Adding subdivision type", "Ajout du type de lotissement")
add("يتم إظافة  نوع الطريق", "Adding road type", "Ajout du type de voie")
add("يتم إظافة  نوع المرفق", "Adding facility type", "Ajout du type d'équipement")
add("يتم إظافة  نوع المنطقة", "Adding zone type", "Ajout du type de zone")
add("يتم إظافة  نوع النشاط", "Adding activity type", "Ajout du type d'activité")
add("المسافة الإجمالية", "Total Distance", "Distance totale")
add("متر", "m", "m")
add("إعادة تحديث القياس", "Reset measurement", "Réinitialiser la mesure")
add("إنهاء", "Finish", "Terminer")
add("تم إنهاء أداة القياس", "Measurement tool ended", "Outil de mesure terminé")
add("متوقفة مؤقتاً", "Paused", "En pause")
add("تمت المتابعة", "Resumed", "Reprise")
add("الحالة", "Status", "Statut")
add("غير قادر على تسجيل الدخول إلى الخادم أو الصورة غير موجودة",
    "Unable to log in to server or image not found",
    "Impossible de se connecter au serveur ou image introuvable")
add("إنشاء قاعدة بيانات المصادقة", "Create auth database", "Créer la base de données d'authentification")
add("الملف المحدد ليس قاعدة بيانات", "Selected file is not a database", "Le fichier sélectionné n'est pas une base de données")
add("الملف المحدد ليس قاعدة بيانات SQLite صالحة",
    "Selected file is not a valid SQLite database",
    "Le fichier sélectionné n'est pas une base SQLite valide")
add("صالحة", "Valid", "Valide")
add("فشل في نسخ الملف", "Failed to copy file", "Échec de la copie du fichier")
add("قاعدة بيانات المصادقة موجودة مسبقاً", "Auth database already exists", "La base de données d'authentification existe déjà")
add("نسخ الملف بنجاح", "File copied successfully", "Fichier copié avec succès")
add("يوجد ملف محدد", "File selected", "Fichier sélectionné")
add("التوزيع حسب الوضعية", "Distribution by Status", "Répartition par statut")
add("التوزيع حسب حالة الترقيم", "Distribution by Numbering State", "Répartition par état de numérotation")
add("العدد", "Count", "Nombre")
add("الوضعية", "Status", "Statut")
add("حفظ ملفك في مستنداتي", "Save file in My Documents", "Enregistrer dans Mes Documents")
add("خريطة ترقيم المداخل أو خريطة اللواحات",
    "Numbering map or panels map",
    "Carte de numérotation ou carte des panneaux")
add("يجب عليك تحديد نوع الخريطة التي تريد طباعتها",
    "You must select the map type to print",
    "Vous devez sélectionner le type de carte à imprimer")
add("الطريق موجود بالفعل", "Road already exists", "La voie existe déjà")
add("المنطقة موجودة بالفعل", "Zone already exists", "La zone existe déjà")
add("تريد مسح خط القياس ؟", "Clear measurement line?", "Effacer la ligne de mesure ?")
add("تمت إضافة هذا الحي بنجاح", "Subdivision added successfully", "Lotissement ajouté avec succès")
add("تمت إضافة هذا الطريق بنجاح", "Road added successfully", "Voie ajoutée avec succès")
add("تمت إضافة هذا المدخل بنجاح", "Entrance added successfully", "Entrée ajoutée avec succès")
add("تمت إضافة هذا المرفق بنجاح", "Facility added successfully", "Équipement ajouté avec succès")
add("تمت إضافة هذه اللوحة بنجاح", "Panel added successfully", "Panneau ajouté avec succès")
add("تمت إضافة هذه المنطقة بنجاح", "Zone added successfully", "Zone ajoutée avec succès")
add("تمسح خط القياس ؟", "Delete measurement line?", "Supprimer la ligne de mesure ?")
add("نعم", "Yes", "Oui")
add("يمكن إضافة الطريق", "Can add road", "Peut ajouter la voie")
add("يمكن إضافة المرفق ، المرفق موجود بالفعل", "Facility already exists, can add", "L'équipement existe déjà, peut ajouter")
add("يمكن إضافة المنطقة", "Can add zone", "Peut ajouter la zone")
add("حفظ تقريرك في مستنداتك", "Save report in My Documents", "Enregistrer le rapport dans Mes Documents")
add("فشل في إنشاء التقرير", "Failed to create report", "Échec de la création du rapport")
add("لا يوجد ملف محدد", "No file selected", "Aucun fichier sélectionné")
add("تم نسخ الملف بنجاح", "File copied successfully", "Fichier copié avec succès")
add("الملف المحدد ليس قاعدة بيانات SQLite صالحة",
    "Selected file is not a valid SQLite database",
    "Le fichier sélectionné n'est pas une base SQLite valide")
add(" هل تريد مسح خط القياس ؟",
    " Do you want to clear the measurement line?",
    " Voulez-vous effacer la ligne de mesure ?")
add(" هل تمسح خط القياس ؟",
    " Clear the measurement line?",
    " Effacer la ligne de mesure ?")
add("لا", "No", "Non")
add("الموقع", "Location", "Emplacement")
add("شكل هندسي", "Geometry", "Géométrie")
add("القطاع", "Sector", "Secteur")
add("النوع", "Type", "Type")
add("لم يتم إظافة  نوع الطريق", "Road type not added", "Type de voie non ajouté")
add("لم يتم إظافة  نوع المنطقة", "Zone type not added", "Type de zone non ajouté")
add("لم يتم إظافة  نوع التجزئة", "Subdivision type not added", "Type de lotissement non ajouté")
add("لم يتم إظافة  نوع المرفق", "Facility type not added", "Type d'équipement non ajouté")
add("لم يتم إظافة  نوع النشاط", "Activity type not added", "Type d'activité non ajouté")
add("لا يمكن إضافة الطريق , الطريق موجود بالفعل",
    "Cannot add road, road already exists",
    "Impossible d'ajouter la voie, elle existe déjà")
add("لا يمكن إضافة المرفق ، المرفق موجود بالفعل",
    "Cannot add facility, facility already exists",
    "Impossible d'ajouter l'équipement, il existe déjà")
add("لا يمكن إضافة المنطقة , المنطقة موجودة بالفعل",
    "Cannot add zone, zone already exists",
    "Impossible d'ajouter la zone, elle existe déjà")
add("تمت إضافة هذه اللوحة بنجاح\n هل تريد مسح خط القياس ؟",
    "Panel added.\nClear measurement line?",
    "Panneau ajouté.\nEffacer la ligne de mesure ?")
add("تمت إضافة هذا المدخل بنجاح\n هل تمسح خط القياس ؟",
    "Entrance added.\nClear measurement line?",
    "Entrée ajoutée.\nEffacer la ligne de mesure ?")
add("تم حفظ ملفك في مستنداتي", "File saved in My Documents", "Fichier enregistré dans Mes Documents")
add("خريطة ترقيم المداخل أو خريطة اللواحات  \n  يجب عليك تحديد نوع الخريطة التي تريد طباعتها",
    "Numbering map or panels map\nYou must select the map type to print",
    "Carte de numérotation ou carte des panneaux\nVous devez sélectionner le type de carte à imprimer")
add("تم إنشاء قاعدة بيانات المصادقة", "Auth database created", "Base de données d'authentification créée")
add("قاعدة بيانات المصادقة موجودة مسبقاً", "Auth database already exists", "La base de données d'authentification existe déjà")
add("غير قادر على تسجيل الدخول إلى الخادم أو الصورة غير موجودة",
    "Unable to log in to server or image not found",
    "Impossible de se connecter au serveur ou image introuvable")

# --- Settings group labels (dynamically created in setup_settings_ui) ---
add("الإعدادات", "Settings", "Paramètres")
add("المظهر:", "Theme:", "Thème :")
add("اللغة:", "Language:", "Langue :")

# --- Scale bar unit labels ---
add("كم", "km", "km")
add("م", "m", "m")

# --- Entity list dialog titles ---
add("المداخل", "Entrances", "Entrées")
add("اللواحات", "Panels", "Panneaux")

# --- Tab titles ---
add("المناطق", "Zones", "Zones")
add("الطرق", "Roads", "Voies")
add("المرافق", "Facilities", "Équipements")
add("التجزئات", "Subdivisions", "Lotissements")
add("الترقيم", "Numbering", "Numérotation")
add("اللوحات", "Panels", "Panneaux")
add("تقرير", "Report", "Rapport")
add("اعدادات", "Settings", "Paramètres")

# --- Tab tooltips ---
add('<html><head/><body><p align="right">المناطق</p></body></html>',
    '<html><head/><body><p align="right">Zones</p></body></html>',
    '<html><head/><body><p align="right">Zones</p></body></html>')
add('<html><head/><body><p>الطرق</p></body></html>',
    '<html><head/><body><p>Roads</p></body></html>',
    '<html><head/><body><p>Voies</p></body></html>')
add('<html><head/><body><p align="right">المرافق</p></body></html>',
    '<html><head/><body><p align="right">Facilities</p></body></html>',
    '<html><head/><body><p align="right">Équipements</p></body></html>')
add('<html><head/><body><p align="right">الأحياء</p></body></html>',
    '<html><head/><body><p align="right">Subdivisions</p></body></html>',
    '<html><head/><body><p align="right">Lotissements</p></body></html>')
add('<html><head/><body><p>الترقيم</p></body></html>',
    '<html><head/><body><p>Numbering</p></body></html>',
    '<html><head/><body><p>Numérotation</p></body></html>')
add('<html><head/><body><p>اللوحات</p></body></html>',
    '<html><head/><body><p>Panels</p></body></html>',
    '<html><head/><body><p>Panneaux</p></body></html>')
add('<html><head/><body><p>تقرير</p></body></html>',
    '<html><head/><body><p>Report</p></body></html>',
    '<html><head/><body><p>Rapport</p></body></html>')
add('<html><head/><body><p>اعدادات</p></body></html>',
    '<html><head/><body><p>Settings</p></body></html>',
    '<html><head/><body><p>Paramètres</p></body></html>')

# --- HTML tooltips ---
add(
    '<html><head/><body><p>حدد نوع الحي</p></body></html>',
    '<html><head/><body><p>Select subdivision type</p></body></html>',
    '<html><head/><body><p>Sélectionner le type de lotissement</p></body></html>',
)
add(
    '<html><head/><body><p>قياس المسافة</p></body></html>',
    '<html><head/><body><p>Measure distance</p></body></html>',
    '<html><head/><body><p>Mesurer la distance</p></body></html>',
)
add(
    '<html><head/><body><p>حدد نوع المرفق</p></body></html>',
    '<html><head/><body><p>Select facility type</p></body></html>',
    '<html><head/><body><p>Sélectionner le type d\'équipement</p></body></html>',
)
add(
    '<html><head/><body><p>ارسم الشكل الهندسي للحي</p></body></html>',
    '<html><head/><body><p>Draw the subdivision geometry</p></body></html>',
    '<html><head/><body><p>Dessiner la géométrie du lotissement</p></body></html>',
)
add(
    '<html><head/><body><p>تحديث الشكل الهندسي للحي</p></body></html>',
    '<html><head/><body><p>Update the subdivision geometry</p></body></html>',
    '<html><head/><body><p>Mettre à jour la géométrie du lotissement</p></body></html>',
)
add(
    '<html><head/><body><p>ارسم الشكل الهندسي للمرفق</p></body></html>',
    '<html><head/><body><p>Draw the facility geometry</p></body></html>',
    '<html><head/><body><p>Dessiner la géométrie de l\'équipement</p></body></html>',
)
add(
    '<html><head/><body><p>تحديث الشكل الهندسي للمدخل</p></body></html>',
    '<html><head/><body><p>Update the entrance geometry</p></body></html>',
    '<html><head/><body><p>Mettre à jour la géométrie de l\'entrée</p></body></html>',
)
add(
    '<html><head/><body><p>تحديث الشكل الهندسي للمرفق</p></body></html>',
    '<html><head/><body><p>Update the facility geometry</p></body></html>',
    '<html><head/><body><p>Mettre à jour la géométrie de l\'équipement</p></body></html>',
)
add(
    '<html><head/><body><p align="right">حدد نوع الطريق</p></body></html>',
    '<html><head/><body><p align="right">Select road type</p></body></html>',
    '<html><head/><body><p align="right">Sélectionner le type de voie</p></body></html>',
)
add(
    '<html><head/><body><p align="right">حدد نوع المنطقة</p></body></html>',
    '<html><head/><body><p align="right">Select zone type</p></body></html>',
    '<html><head/><body><p align="right">Sélectionner le type de zone</p></body></html>',
)
add(
    '<html><head/><body><p align="right">عرض قائمة الطرق</p></body></html>',
    '<html><head/><body><p align="right">View road list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des voies</p></body></html>',
)
add(
    '<html><head/><body><p align="right">عرض قائمة اللوحات</p></body></html>',
    '<html><head/><body><p align="right">View panels list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des panneaux</p></body></html>',
)
add(
    '<html><head/><body><p align="right">عرض قائمة المداخل</p></body></html>',
    '<html><head/><body><p align="right">View entrances list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des entrées</p></body></html>',
)
add(
    '<html><head/><body><p align="right">عرض قائمة المرافق</p></body></html>',
    '<html><head/><body><p align="right">View facilities list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des équipements</p></body></html>',
)
add(
    '<html><head/><body><p align="right">عرض قائمة التجزئات</p></body></html>',
    '<html><head/><body><p align="right">View subdivisions list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des lotissements</p></body></html>',
)
add(
    '<html><head/><body><p>ارسم الشكل الهندسي للمدخل</p><p><br/></p></body></html>',
    '<html><head/><body><p>Draw the entrance geometry</p><p><br/></p></body></html>',
    '<html><head/><body><p>Dessiner la géométrie de l\'entrée</p><p><br/></p></body></html>',
)
add(
    '<html><head/><body><p align="right">ارسم الشكل الهندسي للطريق</p></body></html>',
    '<html><head/><body><p align="right">Draw the road geometry</p></body></html>',
    '<html><head/><body><p align="right">Dessiner la géométrie de la voie</p></body></html>',
)
add(
    '<html><head/><body><p align="right"> رقم القرار الخاص بالتكريس</p></body></html>',
    '<html><head/><body><p align="right">Decision number for dedication</p></body></html>',
    '<html><head/><body><p align="right">N° de décision de consécration</p></body></html>',
)
add(
    '<html><head/><body><p align="right">ارسم الشكل الهندسي للمنطقة</p></body></html>',
    '<html><head/><body><p align="right">Draw the zone geometry</p></body></html>',
    '<html><head/><body><p align="right">Dessiner la géométrie de la zone</p></body></html>',
)
add(
    '<html><head/><body><p align="right">تحديث الشكل الهندسي للطريق</p></body></html>',
    '<html><head/><body><p align="right">Update the road geometry</p></body></html>',
    '<html><head/><body><p align="right">Mettre à jour la géométrie de la voie</p></body></html>',
)
add(
    '<html><head/><body><p align="right">تحديث الشكل الهندسي للمنطقة</p></body></html>',
    '<html><head/><body><p align="right">Update the zone geometry</p></body></html>',
    '<html><head/><body><p align="right">Mettre à jour la géométrie de la zone</p></body></html>',
)
add(
    '<html><head/><body><p align="right">مؤشر توافر الشكل الهندسي للحي</p></body></html>',
    '<html><head/><body><p align="right">Subdivision geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie lotissement</p></body></html>',
)
add(
    '<html><head/><body><p align="right">مؤشر توافر الشكل الهندسي للطريق</p></body></html>',
    '<html><head/><body><p align="right">Road geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie voie</p></body></html>',
)
add(
    '<html><head/><body><p align="right">مؤشر توافر الشكل الهندسي للمدخل</p></body></html>',
    '<html><head/><body><p align="right">Entrance geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie entrée</p></body></html>',
)
add(
    '<html><head/><body><p align="right">مؤشر توافر الشكل الهندسي للمرفق</p></body></html>',
    '<html><head/><body><p align="right">Facility geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie équipement</p></body></html>',
)
add(
    '<html><head/><body><p>اللقب <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Surname <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Prénom <span style=" color:#ff0000;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p align="right">مؤشر توافر الشكل الهندسي للمنطقة</p></body></html>',
    '<html><head/><body><p align="right">Zone geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie zone</p></body></html>',
)
add(
    '<html><head/><body><p>الاسم <span style=" color:#ff0000;">*</span> :</p></body></html>',
    '<html><head/><body><p>First name <span style=" color:#ff0000;">*</span> :</p></body></html>',
    '<html><head/><body><p>Nom <span style=" color:#ff0000;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>البلدية <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Municipality <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Municipalité <span style=" color:#ff0000;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>الولاية <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Wilaya <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Wilaya <span style=" color:#ff0000;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>كلمة السر <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Password <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Mot de passe <span style=" color:#ff0000;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>رقم الهاتف <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Phone number <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Téléphone <span style=" color:#ff0000;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>اسم المستخدم <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Username <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Nom d\'utilisateur <span style=" color:#ff0000;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>البريد الإلكتروني <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>Email <span style=" color:#ff0000;">*</span>:</p></body></html>',
    '<html><head/><body><p>E-mail <span style=" color:#ff0000;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>تحديد الحي على الخريطة لحذفه أو تحديث المعلومات المتعلقة به</p></body></html>',
    '<html><head/><body><p>Select the subdivision on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p>Sélectionner le lotissement sur la carte pour le supprimer ou mettre à jour ses informations</p></body></html>',
)
add(
    '<html><head/><body><p align="right">حفظ المعلومات والشكل الهندسي في قاعدة البيانات</p></body></html>',
    '<html><head/><body><p align="right">Save information and geometry to the database</p></body></html>',
    '<html><head/><body><p align="right">Enregistrer les informations et la géométrie dans la base de données</p></body></html>',
)
add(
    '<html><head/><body><p>تحديد المدخل على الخريطة لحذفه أو تحديث المعلومات المتعلقة به</p></body></html>',
    '<html><head/><body><p>Select the entrance on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p>Sélectionner l\'entrée sur la carte pour la supprimer ou mettre à jour ses informations</p></body></html>',
)
add(
    '<html><head/><body><p align="justify">حفظ المعلومات والشكل الهندسي في قاعدة البيانات</p></body></html>',
    '<html><head/><body><p align="justify">Save information and geometry to the database</p></body></html>',
    '<html><head/><body><p align="justify">Enregistrer les informations et la géométrie dans la base de données</p></body></html>',
)
add(
    '<html><head/><body><p>تحديد المرفق على الخريطة لحذفه أو تحديث المعلومات المتعلقة به</p><p><br/></p></body></html>',
    '<html><head/><body><p>Select the facility on the map to delete or update its information</p><p><br/></p></body></html>',
    '<html><head/><body><p>Sélectionner l\'équipement sur la carte pour le supprimer ou mettre à jour ses informations</p><p><br/></p></body></html>',
)
add(
    '<html><head/><body><p align="right">تحديد الطريق على الخريطة لحذفه أو تحديث المعلومات المتعلقة به</p></body></html>',
    '<html><head/><body><p align="right">Select the road on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p align="right">Sélectionner la voie sur la carte pour la supprimer ou mettre à jour ses informations</p></body></html>',
)
add(
    '<html><head/><body><p align="right">في حالة حدوث خطأ يمكنك استعادة الإصدار السابق من قاعدة البيانات</p></body></html>',
    '<html><head/><body><p align="right">In case of error, you can restore the previous version of the database</p></body></html>',
    '<html><head/><body><p align="right">En cas d\'erreur, vous pouvez restaurer la version précédente de la base de données</p></body></html>',
)
add(
    '<html><head/><body><p align="right">تحديد المنطقة على الخريطة لحذفها أو تحديث المعلومات المتعلقة بها</p></body></html>',
    '<html><head/><body><p align="right">Select the zone on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p align="right">Sélectionner la zone sur la carte pour la supprimer ou mettre à jour ses informations</p></body></html>',
)
add(
    '<html><head/><body><p align="right">إنشاء نسخة من قاعدة البيانات</p><p align="right"> لاسترادها في حالة حدوث خطأ</p></body></html>',
    '<html><head/><body><p align="right">Create a backup of the database</p><p align="right"> to restore it in case of error</p></body></html>',
    '<html><head/><body><p align="right">Créer une copie de sauvegarde de la base de données</p><p align="right"> pour la restaurer en cas d\'erreur</p></body></html>',
)
# --- Long instructional tooltips ---
add(
    '<html><head/><body><p align="right">يجب ألا يكون اسم الطريق متسلسلا مع نوع الطريق مثل<span style=" font-weight:600;"> شارع ديدوش مراد </span></p><p align="right"><span style=" font-weight:600;">نوع الطريق :</span> شارع</p><p align="right"><span style=" font-weight:600;">اسم الطريق :</span> ديدوش مراد</p></body></html>',
    '<html><head/><body><p align="right">The road name should not be concatenated with the road type e.g.<span style=" font-weight:600;"> Rue Didouche Mourad </span></p><p align="right"><span style=" font-weight:600;">Road Type :</span> Rue</p><p align="right"><span style=" font-weight:600;">Road Name :</span> Didouche Mourad</p></body></html>',
    '<html><head/><body><p align="right">Le nom de la voie ne doit pas être concaténé avec le type de voie comme<span style=" font-weight:600;"> Rue Didouche Mourad </span></p><p align="right"><span style=" font-weight:600;">Type de voie :</span> Rue</p><p align="right"><span style=" font-weight:600;">Nom de voie :</span> Didouche Mourad</p></body></html>',
)
add(
    '<html><head/><body><p align="right">يجب ألا يكون اسم المرفق متسلسلا مع نوع المرفق مثل<span style=" font-weight:600;"> مستشفى بشير منتوري </span></p><p align="right"><span style=" font-weight:600;">نوع المرفق :</span>مستشفى</p><p align="right"><span style=" font-weight:600;">اسم المرفق :</span> شير منتوري</p></body></html>',
    '<html><head/><body><p align="right">The facility name should not be concatenated with the facility type e.g.<span style=" font-weight:600;"> Bachir Mentouri Hospital </span></p><p align="right"><span style=" font-weight:600;">Facility Type :</span> Hospital</p><p align="right"><span style=" font-weight:600;">Facility Name :</span> Bachir Mentouri</p></body></html>',
    '<html><head/><body><p align="right">Le nom de l\'équipement ne doit pas être concaténé avec le type d\'équipement comme<span style=" font-weight:600;"> Hôpital Bachir Mentouri </span></p><p align="right"><span style=" font-weight:600;">Type d\'équipement :</span> Hôpital</p><p align="right"><span style=" font-weight:600;">Nom d\'équipement :</span> Bachir Mentouri</p></body></html>',
)
add(
    '<html><head/><body><p align="right">يجب ألا يكون اسم المنطقة متسلسلا مع نوع المنطقة مثل<span style=" font-weight:600;"> منطقة الصناعية دار البيضاء</span></p><p align="right"><span style=" font-weight:600;">نوع منطقة :</span> منطقة صناعية</p><p align="right"><span style=" font-weight:600;">اسم منطقة :</span> دار البيضاء</p></body></html>',
    '<html><head/><body><p align="right">The zone name should not be concatenated with the zone type e.g.<span style=" font-weight:600;"> Industrial Zone Dar El Beida</span></p><p align="right"><span style=" font-weight:600;">Zone Type :</span> Industrial Zone</p><p align="right"><span style=" font-weight:600;">Zone Name :</span> Dar El Beida</p></body></html>',
    '<html><head/><body><p align="right">Le nom de la zone ne doit pas être concaténé avec le type de zone comme<span style=" font-weight:600;"> Zone Industrielle Dar El Beida</span></p><p align="right"><span style=" font-weight:600;">Type de zone :</span> Zone Industrielle</p><p align="right"><span style=" font-weight:600;">Nom de zone :</span> Dar El Beida</p></body></html>',
)
add(
    '<html><head/><body><p align="right">يجب ألا يكون اسم الحي متسلسلا مع نوع الحي مثل<span style=" font-weight:600;"> تعاونية البرتقال </span></p><p align="right"><span style=" font-weight:600;">نوع الحي : </span>تعاونية</p><p align="right"><span style=" font-weight:600;">اسم الحي :</span><span style=" font-weight:600;"/>البرتقال</p></body></html>',
    '<html><head/><body><p align="right">The subdivision name should not be concatenated with the subdivision type e.g.<span style=" font-weight:600;"> Cooperatie El Bortokal </span></p><p align="right"><span style=" font-weight:600;">Subdivision Type :</span> Cooperatie</p><p align="right"><span style=" font-weight:600;">Subdivision Name :</span> El Bortokal</p></body></html>',
    '<html><head/><body><p align="right">Le nom du lotissement ne doit pas être concaténé avec le type de lotissement comme<span style=" font-weight:600;"> Cooperatie El Bortokal </span></p><p align="right"><span style=" font-weight:600;">Type de lotissement : </span>Cooperatie</p><p align="right"><span style=" font-weight:600;">Nom de lotissement :</span><span style=" font-weight:600;"/>El Bortokal</p></body></html>',
)

def write_ts(lang_code, translations, path):
    lines = [TS_HEADER.format(lang=lang_code)]
    for ar_text in sorted(translations.keys()):
        en_text = translations[ar_text]
        lines.append("    <message>")
        lines.append(f"        <source>{_escape(ar_text)}</source>")
        lines.append(f"        <translation>{_escape(en_text)}</translation>")
        lines.append("    </message>")
    lines.append(TS_FOOTER)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"Wrote {len(translations)} messages to {path}")

def _escape(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

write_ts("en", EN, "i18n/RNA_en.ts")
write_ts("fr", FR, "i18n/RNA_fr.ts")
print("Done!")
