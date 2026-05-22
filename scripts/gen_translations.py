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

add("Save", "Save", "Enregistrer")
add("Dark", "Dark", "Sombre")
add("Light", "Light", "Clair")
add("Name:", "Name:", "Nom :")
add("Number:", "Number:", "Numéro :")
add("Category:", "Category:", "Catégorie :")
add("Type:", "Type:", "Type :")
add("Type:", "Type:", "Type :")
add("Status:", "Status:", "État :")
add("Cancel", "Cancel", "Annuler")
add("Update", "Update", "Mettre à jour")
add("Category:", "Category:", "Catégorie :")
add("Duplicate:", "Duplicate:", "Doublon :")
add("Logout", "Logout", "Quitter")
add("Login", "Login", "Connexion")
add("Language:", "Language:", "Langue :")
add("Facility", "Facility", "Équipement")
add("Date", "Date", "Date")
add("Theme:", "Theme:", "Thème :")
add("Settings", "Settings", "Paramètres")
add("Start Drawing", "Start Drawing", "Commencer le dessin")
add("Select Road", "Select Road", "Sélectionner la voie")
add("Select Entrance", "Select Entrance", "Sélectionner l'entrée")
add("Select Reference", "Select Reference", "Sélectionner la référence")
add("Select Facility", "Select Facility", "Sélectionner l'équipement")
add("Plan Number", "Plan Number", "Numéro du plan")
add("Password:", "Password:", "Mot de passe :")
add("Draw Road", "Draw Road", "Dessiner la voie")
add("Draw Entrance", "Draw Entrance", "Dessiner l'entrée")
add("Draw Facility", "Draw Facility", "Dessiner l'équipement")
add("Select Subdivision", "Select Subdivision", "Sélectionner le lotissement")
add("Select Zone", "Select Zone", "Sélectionner la zone")
add("Select Geometry", "Select Geometry", "Sélectionner la géométrie")
add("Road List", "Road List", "Liste des voies")
add("Done by", "Done by", "Réalisé par")
add("Order Form", "Order Form", "Bon de commande")
add("Decision No.:", "Decision No.:", "N° de décision :")
add("Road Type:", "Road Type:", "Type de voie :")
add("Reference Type:", "Reference Type:", "Type de référence :")
add("Add User", "Add User", "Ajouter un utilisateur")
add("Draw Subdivision", "Draw Subdivision", "Dessiner le lotissement")
add("Draw Zone", "Draw Zone", "Dessiner la zone")
add("Update Road", "Update Road", "Mettre à jour la voie")
add("Update Entrance", "Update Entrance", "Mettre à jour l'entrée")
add("Update Facility", "Update Facility", "Mettre à jour l'équipement")
add("Sign In", "Sign In", "Se connecter")
add("Measure Distance", "Measure Distance", "Mesurer la distance")
add("Select Map:", "Select Map:", "Sélectionner la carte :")
add("Subdivision Type:", "Subdivision Type:", "Type de lotissement :")
add("Zone Type:", "Zone Type:", "Type de zone :")
add("Generate Report", "Generate Report", "Générer le rapport")
add("Generate Map", "Generate Map", "Générer la carte")
add("Update Subdivision", "Update Subdivision", "Mettre à jour le lotissement")
add("Update Zone", "Update Zone", "Mettre à jour la zone")
add("Entrance List", "Entrance List", "Liste des entrées")
add("Facility List", "Facility List", "Liste des équipements")
add("Study Area", "Study Area", "Zone d'étude")
add("Username:", "Username:", "Nom d'utilisateur :")
add("Mounting Status:", "Mounting Status:", "État de montage :")
add("Subdivisions List", "Subdivisions List", "Liste des lotissements")
add("Panels List", "Panels List", "Liste des panneaux")
add("Generate Numbering Map", "Generate Numbering Map", "Carte de numérotation")
add("Generate Panels Map", "Generate Panels Map", "Carte des panneaux")
add("Geometry Status:", "Geometry Status:", "Disponibilité géométrie :")
add("Restore Database", "Restore Database", "Restaurer la base de données")
add("Entrance-related Activity", "Entrance-related Activity", "Activité liée à l'entrée")
add("Database Backup", "Database Backup", "Sauvegarde BD")
add("Space Applications Center 2025 ©", "Space Applications Center 2025 ©", "Centre des Applications Spatiales 2025 ©")
add("Create Database Backup", "Create Database Backup", "Créer une sauvegarde BD")
add("Please restart QGIS to apply the language change", "Please restart QGIS to apply the language change", "Veuillez redémarrer QGIS pour appliquer le changement de langue")

# --- List / entity dialog labels ---
add("Name", "Name", "Nom")
add("Number", "Number", "Numéro")
add("Type", "Type", "Type")
add("Status", "Status", "Statut")
add("ID", "ID", "ID")
add("Decision No.", "Decision No.", "N° décision")
add("Road", "Road", "Voie")
add("Subdivision", "Subdivision", "Lotissement")
add("Duplicate", "Duplicate", "Doublon")
add("User", "User", "Utilisateur")
add("Dimensions", "Dimensions", "Dimensions")
add("Reference Type", "Reference Type", "Type référence")
add("Status", "Status", "Statut")
add("Label", "Label", "Étiquette")
add("My Municipality", "My Municipality", "Ma Municipalité")
add("Previous", "Previous", "Précédent")
add("Next", "Next", "Suivant")
add("Page", "Page", "Page")
add("List of ", "List of ", "Liste des ")
add("Entrances", "Entrances", "Entrées")
add("Panels", "Panels", "Panneaux")
add("No Activity", "No Activity", "Aucune activité")
add("A3 Paper for Fieldwork", "A3 Paper for Fieldwork", "Papier A3 pour travail terrain")
add("A0 Paper for Administration", "A0 Paper for Administration", "Papier A0 pour administration")

# --- Database seed data (road types) ---
add("Street", "Street", "Rue")
add("Alley", "Alley", "Ruelle")
add("Lane", "Lane", "Impasse")
add("Passage", "Passage", "Passage")
add("Dirt Road", "Dirt Road", "Chemin de terre")
add("Dead End", "Dead End", "Impasse")
add("Cut-through", "Cut-through", "Passage coupé")
add("Path", "Path", "Sentier")
add("Sloped Road", "Sloped Road", "Route en pente")
add("Slope", "Slope", "Pente")
add("Steps", "Steps", "Escalier")
add("Footbridge", "Footbridge", "Passerelle")
add("Pedestrian Bridge", "Pedestrian Bridge", "Pont piéton")
add("Boulevard", "Boulevard", "Boulevard")
add("Private Road", "Private Road", "Voie privée")
add("Passageway", "Passageway", "Passage")
add("Municipal Path", "Municipal Path", "Chemin communal")
add("Path", "Path", "Piste")
add("Provincial Path", "Provincial Path", "Chemin de wilaya")
add("National Road", "National Road", "Route nationale")

# --- Database seed data (zone types) ---
add("Activity Zone", "Activity Zone", "Zone d'activités")
add("Industrial Zone", "Industrial Zone", "Zone industrielle")
add("Urban Pole", "Urban Pole", "Pôle urbain")
add("Zone", "Zone", "Zone")
add("Roundabout", "Roundabout", "Rond-point")
add("Village", "Village", "Village")
add("Hamlet", "Hamlet", "Hameau")
add("Neighborhood", "Neighborhood", "Quartier")

# --- Database seed data (subdivision types) ---
add("Housing Complex", "Housing Complex", "Complexe résidentiel")
add("Cooperative", "Cooperative", "Coopérative")
add("Compound", "Compound", "Complexe")
add("Division", "Division", "Division")
add("Residence", "Residence", "Résidence")
add("Group", "Group", "Groupe")
add("Residential Neighborhood", "Residential Neighborhood", "Quartier résidentiel")
add("Real Estate Complex", "Real Estate Complex", "Promotion immobilière")
add("Subdivision", "Subdivision", "Lotissement")

# --- Database seed data (mounting statuses) ---
add("Programmed", "Programmed", "Programmé")
add("Installed", "Installed", "Installé")
add("To Be Corrected", "To Be Corrected", "À corriger")
add("To Be Moved", "To Be Moved", "À déplacer")

# --- Database seed data (numbering states) ---
add("Programmed", "Programmed", "Programmé")
add("Numbered and Matching", "Numbered and Matching", "Numéroté et conforme")
add("Numbered and Mismatched", "Numbered and Mismatched", "Numéroté et non conforme")
add("Reserved", "Reserved", "Réservé")

# --- Messages & notifications ---
add("Road updated successfully", "Road updated successfully", "Voie mise à jour avec succès")
add("Cannot update road", "Cannot update road", "Impossible de mettre à jour la voie")
add("Facility updated successfully", "Facility updated successfully", "Équipement mis à jour avec succès")
add("Cannot update facility", "Cannot update facility", "Impossible de mettre à jour l'équipement")
add("Subdivision updated successfully", "Subdivision updated successfully", "Lotissement mis à jour avec succès")
add("Cannot update subdivision", "Cannot update subdivision", "Impossible de mettre à jour le lotissement")
add("Zone updated successfully", "Zone updated successfully", "Zone mise à jour avec succès")
add("Cannot update zone", "Cannot update zone", "Impossible de mettre à jour la zone")
add("Panel updated successfully", "Panel updated successfully", "Panneau mis à jour avec succès")
add("Cannot update panel", "Cannot update panel", "Impossible de mettre à jour le panneau")
add("Entrance updated successfully", "Entrance updated successfully", "Entrée mise à jour avec succès")
add("Reference type not selected", "Reference type not selected", "Type de référence non sélectionné")
add("Road type added", "Road type added", "Type de voie ajouté")
add("Zone type added", "Zone type added", "Type de zone ajouté")
add("Subdivision type added", "Subdivision type added", "Type de lotissement ajouté")
add("Facility type added", "Facility type added", "Type d'équipement ajouté")
add("Activity type added", "Activity type added", "Type d'activité ajouté")
add("Adding subdivision type", "Adding subdivision type", "Ajout du type de lotissement")
add("Adding road type", "Adding road type", "Ajout du type de voie")
add("Adding facility type", "Adding facility type", "Ajout du type d'équipement")
add("Adding zone type", "Adding zone type", "Ajout du type de zone")
add("Adding activity type", "Adding activity type", "Ajout du type d'activité")
add("Total Distance", "Total Distance", "Distance totale")
add("m", "m", "m")
add("Reset measurement", "Reset measurement", "Réinitialiser la mesure")
add("Finish", "Finish", "Terminer")
add("Measurement tool ended", "Measurement tool ended", "Outil de mesure terminé")
add("Paused", "Paused", "En pause")
add("Resumed", "Resumed", "Reprise")
add("Status", "Status", "Statut")
add("Unable to log in to server or image not found",
    "Unable to log in to server or image not found",
    "Impossible de se connecter au serveur ou image introuvable")
add("Create auth database", "Create auth database", "Créer la base de données d'authentification")
add("Selected file is not a database", "Selected file is not a database", "Le fichier sélectionné n'est pas une base de données")
add("Selected file is not a valid SQLite database",
    "Selected file is not a valid SQLite database",
    "Le fichier sélectionné n'est pas une base SQLite valide")
add("Valid", "Valid", "Valide")
add("Failed to copy file", "Failed to copy file", "Échec de la copie du fichier")
add("Auth database already exists", "Auth database already exists", "La base de données d'authentification existe déjà")
add("File copied successfully", "File copied successfully", "Fichier copié avec succès")
add("File selected", "File selected", "Fichier sélectionné")
add("Distribution by Status", "Distribution by Status", "Répartition par statut")
add("Distribution by Numbering State", "Distribution by Numbering State", "Répartition par état de numérotation")
add("Count", "Count", "Nombre")
add("Status", "Status", "Statut")
add("Save file in My Documents", "Save file in My Documents", "Enregistrer dans Mes Documents")
add("Numbering map or panels map",
    "Numbering map or panels map",
    "Carte de numérotation ou carte des panneaux")
add("You must select the map type to print",
    "You must select the map type to print",
    "Vous devez sélectionner le type de carte à imprimer")
add("Road already exists", "Road already exists", "La voie existe déjà")
add("Zone already exists", "Zone already exists", "La zone existe déjà")
add("Clear measurement line?", "Clear measurement line?", "Effacer la ligne de mesure ?")
add("Subdivision added successfully", "Subdivision added successfully", "Lotissement ajouté avec succès")
add("Road added successfully", "Road added successfully", "Voie ajoutée avec succès")
add("Entrance added successfully", "Entrance added successfully", "Entrée ajoutée avec succès")
add("Facility added successfully", "Facility added successfully", "Équipement ajouté avec succès")
add("Panel added successfully", "Panel added successfully", "Panneau ajouté avec succès")
add("Zone added successfully", "Zone added successfully", "Zone ajoutée avec succès")
add("Delete measurement line?", "Delete measurement line?", "Supprimer la ligne de mesure ?")
add("Yes", "Yes", "Oui")
add("Can add road", "Can add road", "Peut ajouter la voie")
add("Facility already exists, can add", "Facility already exists, can add", "L'équipement existe déjà, peut ajouter")
add("Can add zone", "Can add zone", "Peut ajouter la zone")
add("Save report in My Documents", "Save report in My Documents", "Enregistrer le rapport dans Mes Documents")
add("Failed to create report", "Failed to create report", "Échec de la création du rapport")
add("No file selected", "No file selected", "Aucun fichier sélectionné")
add("File copied successfully", "File copied successfully", "Fichier copié avec succès")
add("Selected file is not a valid SQLite database",
    "Selected file is not a valid SQLite database",
    "Le fichier sélectionné n'est pas une base SQLite valide")
add(" Do you want to clear the measurement line?",
    " Do you want to clear the measurement line?",
    " Voulez-vous effacer la ligne de mesure ?")
add(" Clear the measurement line?",
    " Clear the measurement line?",
    " Effacer la ligne de mesure ?")
add("No", "No", "Non")
add("Location", "Location", "Emplacement")
add("Geometry", "Geometry", "Géométrie")
add("Sector", "Sector", "Secteur")
add("Type", "Type", "Type")
add("Road type not added", "Road type not added", "Type de voie non ajouté")
add("Zone type not added", "Zone type not added", "Type de zone non ajouté")
add("Subdivision type not added", "Subdivision type not added", "Type de lotissement non ajouté")
add("Facility type not added", "Facility type not added", "Type d'équipement non ajouté")
add("Activity type not added", "Activity type not added", "Type d'activité non ajouté")
add("Cannot add road, road already exists",
    "Cannot add road, road already exists",
    "Impossible d'ajouter la voie, elle existe déjà")
add("Cannot add facility, facility already exists",
    "Cannot add facility, facility already exists",
    "Impossible d'ajouter l'équipement, il existe déjà")
add("Cannot add zone, zone already exists",
    "Cannot add zone, zone already exists",
    "Impossible d'ajouter la zone, elle existe déjà")
add("Panel added.\nClear measurement line?",
    "Panel added.\nClear measurement line?",
    "Panneau ajouté.\nEffacer la ligne de mesure ?")
add("Entrance added.\nClear measurement line?",
    "Entrance added.\nClear measurement line?",
    "Entrée ajoutée.\nEffacer la ligne de mesure ?")
add("File saved in My Documents", "File saved in My Documents", "Fichier enregistré dans Mes Documents")
add("Numbering map or panels map\nYou must select the map type to print",
    "Numbering map or panels map\nYou must select the map type to print",
    "Carte de numérotation ou carte des panneaux\nVous devez sélectionner le type de carte à imprimer")
add("Auth database created", "Auth database created", "Base de données d'authentification créée")
add("Auth database already exists", "Auth database already exists", "La base de données d'authentification existe déjà")
add("Unable to log in to server or image not found",
    "Unable to log in to server or image not found",
    "Impossible de se connecter au serveur ou image introuvable")

# --- Settings group labels (dynamically created in setup_settings_ui) ---
add("Settings", "Settings", "Paramètres")
add("Theme:", "Theme:", "Thème :")
add("Language:", "Language:", "Langue :")

# --- Scale bar unit labels ---
add("km", "km", "km")
add("m", "m", "m")

# --- Entity list dialog titles ---
add("Entrances", "Entrances", "Entrées")
add("Panels", "Panels", "Panneaux")

# --- Tab titles ---
add("Zones", "Zones", "Zones")
add("Roads", "Roads", "Voies")
add("Facilities", "Facilities", "Équipements")
add("Subdivisions", "Subdivisions", "Lotissements")
add("Numbering", "Numbering", "Numérotation")
add("Panels", "Panels", "Panneaux")
add("Report", "Report", "Rapport")
add("Settings", "Settings", "Paramètres")

# --- Tab tooltips ---
add('<html><head/><body><p align="right">Zones</p></body></html>',
    '<html><head/><body><p align="right">Zones</p></body></html>',
    '<html><head/><body><p align="right">Zones</p></body></html>')
add('<html><head/><body><p>Roads</p></body></html>',
    '<html><head/><body><p>Roads</p></body></html>',
    '<html><head/><body><p>Voies</p></body></html>')
add('<html><head/><body><p align="right">Facilities</p></body></html>',
    '<html><head/><body><p align="right">Facilities</p></body></html>',
    '<html><head/><body><p align="right">Équipements</p></body></html>')
add('<html><head/><body><p align="right">Subdivisions</p></body></html>',
    '<html><head/><body><p align="right">Subdivisions</p></body></html>',
    '<html><head/><body><p align="right">Lotissements</p></body></html>')
add('<html><head/><body><p>Numbering</p></body></html>',
    '<html><head/><body><p>Numbering</p></body></html>',
    '<html><head/><body><p>Numérotation</p></body></html>')
add('<html><head/><body><p>Panels</p></body></html>',
    '<html><head/><body><p>Panels</p></body></html>',
    '<html><head/><body><p>Panneaux</p></body></html>')
add('<html><head/><body><p>Report</p></body></html>',
    '<html><head/><body><p>Report</p></body></html>',
    '<html><head/><body><p>Rapport</p></body></html>')
add('<html><head/><body><p>Settings</p></body></html>',
    '<html><head/><body><p>Settings</p></body></html>',
    '<html><head/><body><p>Paramètres</p></body></html>')

# --- HTML tooltips ---
add(
    '<html><head/><body><p>Select subdivision type</p></body></html>',
    '<html><head/><body><p>Select subdivision type</p></body></html>',
    '<html><head/><body><p>Sélectionner le type de lotissement</p></body></html>',
)
add(
    '<html><head/><body><p>Measure distance</p></body></html>',
    '<html><head/><body><p>Measure distance</p></body></html>',
    '<html><head/><body><p>Mesurer la distance</p></body></html>',
)
add(
    '<html><head/><body><p>Select facility type</p></body></html>',
    '<html><head/><body><p>Select facility type</p></body></html>',
    '<html><head/><body><p>Sélectionner le type d\'équipement</p></body></html>',
)
add(
    '<html><head/><body><p>Draw the subdivision geometry</p></body></html>',
    '<html><head/><body><p>Draw the subdivision geometry</p></body></html>',
    '<html><head/><body><p>Dessiner la géométrie du lotissement</p></body></html>',
)
add(
    '<html><head/><body><p>Update the subdivision geometry</p></body></html>',
    '<html><head/><body><p>Update the subdivision geometry</p></body></html>',
    '<html><head/><body><p>Mettre à jour la géométrie du lotissement</p></body></html>',
)
add(
    '<html><head/><body><p>Draw the facility geometry</p></body></html>',
    '<html><head/><body><p>Draw the facility geometry</p></body></html>',
    '<html><head/><body><p>Dessiner la géométrie de l\'équipement</p></body></html>',
)
add(
    '<html><head/><body><p>Update the entrance geometry</p></body></html>',
    '<html><head/><body><p>Update the entrance geometry</p></body></html>',
    '<html><head/><body><p>Mettre à jour la géométrie de l\'entrée</p></body></html>',
)
add(
    '<html><head/><body><p>Update the facility geometry</p></body></html>',
    '<html><head/><body><p>Update the facility geometry</p></body></html>',
    '<html><head/><body><p>Mettre à jour la géométrie de l\'équipement</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Select road type</p></body></html>',
    '<html><head/><body><p align="right">Select road type</p></body></html>',
    '<html><head/><body><p align="right">Sélectionner le type de voie</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Select zone type</p></body></html>',
    '<html><head/><body><p align="right">Select zone type</p></body></html>',
    '<html><head/><body><p align="right">Sélectionner le type de zone</p></body></html>',
)
add(
    '<html><head/><body><p align="right">View road list</p></body></html>',
    '<html><head/><body><p align="right">View road list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des voies</p></body></html>',
)
add(
    '<html><head/><body><p align="right">View panels list</p></body></html>',
    '<html><head/><body><p align="right">View panels list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des panneaux</p></body></html>',
)
add(
    '<html><head/><body><p align="right">View entrances list</p></body></html>',
    '<html><head/><body><p align="right">View entrances list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des entrées</p></body></html>',
)
add(
    '<html><head/><body><p align="right">View facilities list</p></body></html>',
    '<html><head/><body><p align="right">View facilities list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des équipements</p></body></html>',
)
add(
    '<html><head/><body><p align="right">View subdivisions list</p></body></html>',
    '<html><head/><body><p align="right">View subdivisions list</p></body></html>',
    '<html><head/><body><p align="right">Afficher la liste des lotissements</p></body></html>',
)
add(
    '<html><head/><body><p>Draw the entrance geometry</p><p><br/></p></body></html>',
    '<html><head/><body><p>Draw the entrance geometry</p><p><br/></p></body></html>',
    '<html><head/><body><p>Dessiner la géométrie de l\'entrée</p><p><br/></p></body></html>',
)
add(
    '<html><head/><body><p align="right">Draw the road geometry</p></body></html>',
    '<html><head/><body><p align="right">Draw the road geometry</p></body></html>',
    '<html><head/><body><p align="right">Dessiner la géométrie de la voie</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Decision number for dedication</p></body></html>',
    '<html><head/><body><p align="right">Decision number for dedication</p></body></html>',
    '<html><head/><body><p align="right">N° de décision de consécration</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Draw the zone geometry</p></body></html>',
    '<html><head/><body><p align="right">Draw the zone geometry</p></body></html>',
    '<html><head/><body><p align="right">Dessiner la géométrie de la zone</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Update the road geometry</p></body></html>',
    '<html><head/><body><p align="right">Update the road geometry</p></body></html>',
    '<html><head/><body><p align="right">Mettre à jour la géométrie de la voie</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Update the zone geometry</p></body></html>',
    '<html><head/><body><p align="right">Update the zone geometry</p></body></html>',
    '<html><head/><body><p align="right">Mettre à jour la géométrie de la zone</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Subdivision geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Subdivision geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie lotissement</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Road geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Road geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie voie</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Entrance geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Entrance geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie entrée</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Facility geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Facility geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie équipement</p></body></html>',
)
add(
    '<html><head/><body><p>Surname <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Surname <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Prénom <span style=" color:red;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Zone geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Zone geometry availability</p></body></html>',
    '<html><head/><body><p align="right">Disponibilité géométrie zone</p></body></html>',
)
add(
    '<html><head/><body><p>First name <span style=" color:red;">*</span> :</p></body></html>',
    '<html><head/><body><p>First name <span style=" color:red;">*</span> :</p></body></html>',
    '<html><head/><body><p>Nom <span style=" color:red;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>Municipality <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Municipality <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Municipalité <span style=" color:red;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>Wilaya <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Wilaya <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Wilaya <span style=" color:red;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>Password <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Password <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Mot de passe <span style=" color:red;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>Phone number <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Phone number <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Téléphone <span style=" color:red;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>Username <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Username <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Nom d\'utilisateur <span style=" color:red;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>Email <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>Email <span style=" color:red;">*</span>:</p></body></html>',
    '<html><head/><body><p>E-mail <span style=" color:red;">*</span> :</p></body></html>',
)
add(
    '<html><head/><body><p>Select the subdivision on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p>Select the subdivision on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p>Sélectionner le lotissement sur la carte pour le supprimer ou mettre à jour ses informations</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Save information and geometry to the database</p></body></html>',
    '<html><head/><body><p align="right">Save information and geometry to the database</p></body></html>',
    '<html><head/><body><p align="right">Enregistrer les informations et la géométrie dans la base de données</p></body></html>',
)
add(
    '<html><head/><body><p>Select the entrance on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p>Select the entrance on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p>Sélectionner l\'entrée sur la carte pour la supprimer ou mettre à jour ses informations</p></body></html>',
)
add(
    '<html><head/><body><p align="justify">Save information and geometry to the database</p></body></html>',
    '<html><head/><body><p align="justify">Save information and geometry to the database</p></body></html>',
    '<html><head/><body><p align="justify">Enregistrer les informations et la géométrie dans la base de données</p></body></html>',
)
add(
    '<html><head/><body><p>Select the facility on the map to delete or update its information</p><p><br/></p></body></html>',
    '<html><head/><body><p>Select the facility on the map to delete or update its information</p><p><br/></p></body></html>',
    '<html><head/><body><p>Sélectionner l\'équipement sur la carte pour le supprimer ou mettre à jour ses informations</p><p><br/></p></body></html>',
)
add(
    '<html><head/><body><p align="right">Select the road on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p align="right">Select the road on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p align="right">Sélectionner la voie sur la carte pour la supprimer ou mettre à jour ses informations</p></body></html>',
)
add(
    '<html><head/><body><p align="right">In case of error, you can restore the previous version of the database</p></body></html>',
    '<html><head/><body><p align="right">In case of error, you can restore the previous version of the database</p></body></html>',
    '<html><head/><body><p align="right">En cas d\'erreur, vous pouvez restaurer la version précédente de la base de données</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Select the zone on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p align="right">Select the zone on the map to delete or update its information</p></body></html>',
    '<html><head/><body><p align="right">Sélectionner la zone sur la carte pour la supprimer ou mettre à jour ses informations</p></body></html>',
)
add(
    '<html><head/><body><p align="right">Create a backup of the database</p><p align="right"> to restore it in case of error</p></body></html>',
    '<html><head/><body><p align="right">Create a backup of the database</p><p align="right"> to restore it in case of error</p></body></html>',
    '<html><head/><body><p align="right">Créer une copie de sauvegarde de la base de données</p><p align="right"> pour la restaurer en cas d\'erreur</p></body></html>',
)
# --- Long instructional tooltips ---
add(
    '<html><head/><body><p align="right">The road name should not be concatenated with the road type e.g.<span style=" font-weight:600;"> Rue Didouche Mourad </span></p><p align="right"><span style=" font-weight:600;">Road Type :</span> Rue</p><p align="right"><span style=" font-weight:600;">Road Name :</span> Didouche Mourad</p></body></html>',
    '<html><head/><body><p align="right">The road name should not be concatenated with the road type e.g.<span style=" font-weight:600;"> Rue Didouche Mourad </span></p><p align="right"><span style=" font-weight:600;">Road Type :</span> Rue</p><p align="right"><span style=" font-weight:600;">Road Name :</span> Didouche Mourad</p></body></html>',
    '<html><head/><body><p align="right">Le nom de la voie ne doit pas être concaténé avec le type de voie comme<span style=" font-weight:600;"> Rue Didouche Mourad </span></p><p align="right"><span style=" font-weight:600;">Type de voie :</span> Rue</p><p align="right"><span style=" font-weight:600;">Nom de voie :</span> Didouche Mourad</p></body></html>',
)
add(
    '<html><head/><body><p align="right">The facility name should not be concatenated with the facility type e.g.<span style=" font-weight:600;"> Bachir Mentouri Hospital </span></p><p align="right"><span style=" font-weight:600;">Facility Type :</span> Hospital</p><p align="right"><span style=" font-weight:600;">Facility Name :</span> Bachir Mentouri</p></body></html>',
    '<html><head/><body><p align="right">The facility name should not be concatenated with the facility type e.g.<span style=" font-weight:600;"> Bachir Mentouri Hospital </span></p><p align="right"><span style=" font-weight:600;">Facility Type :</span> Hospital</p><p align="right"><span style=" font-weight:600;">Facility Name :</span> Bachir Mentouri</p></body></html>',
    '<html><head/><body><p align="right">Le nom de l\'équipement ne doit pas être concaténé avec le type d\'équipement comme<span style=" font-weight:600;"> Hôpital Bachir Mentouri </span></p><p align="right"><span style=" font-weight:600;">Type d\'équipement :</span> Hôpital</p><p align="right"><span style=" font-weight:600;">Nom d\'équipement :</span> Bachir Mentouri</p></body></html>',
)
add(
    '<html><head/><body><p align="right">The zone name should not be concatenated with the zone type e.g.<span style=" font-weight:600;"> Industrial Zone Dar El Beida</span></p><p align="right"><span style=" font-weight:600;">Zone Type :</span> Industrial Zone</p><p align="right"><span style=" font-weight:600;">Zone Name :</span> Dar El Beida</p></body></html>',
    '<html><head/><body><p align="right">The zone name should not be concatenated with the zone type e.g.<span style=" font-weight:600;"> Industrial Zone Dar El Beida</span></p><p align="right"><span style=" font-weight:600;">Zone Type :</span> Industrial Zone</p><p align="right"><span style=" font-weight:600;">Zone Name :</span> Dar El Beida</p></body></html>',
    '<html><head/><body><p align="right">Le nom de la zone ne doit pas être concaténé avec le type de zone comme<span style=" font-weight:600;"> Zone Industrielle Dar El Beida</span></p><p align="right"><span style=" font-weight:600;">Type de zone :</span> Zone Industrielle</p><p align="right"><span style=" font-weight:600;">Nom de zone :</span> Dar El Beida</p></body></html>',
)
add(
    '<html><head/><body><p align="right">The subdivision name should not be concatenated with the subdivision type e.g.<span style=" font-weight:600;"> Cooperatie El Bortokal </span></p><p align="right"><span style=" font-weight:600;">Subdivision Type :</span> Cooperatie</p><p align="right"><span style=" font-weight:600;">Subdivision Name :</span> El Bortokal</p></body></html>',
    '<html><head/><body><p align="right">The subdivision name should not be concatenated with the subdivision type e.g.<span style=" font-weight:600;"> Cooperatie El Bortokal </span></p><p align="right"><span style=" font-weight:600;">Subdivision Type :</span> Cooperatie</p><p align="right"><span style=" font-weight:600;">Subdivision Name :</span> El Bortokal</p></body></html>',
    '<html><head/><body><p align="right">Le nom du lotissement ne doit pas être concaténé avec le type de lotissement comme<span style=" font-weight:600;"> Cooperatie El Bortokal </span></p><p align="right"><span style=" font-weight:600;">Type de lotissement : </span>Cooperatie</p><p align="right"><span style=" font-weight:600;">Nom de lotissement :</span><span style=" font-weight:600;"/>El Bortokal</p></body></html>',
)

# --- Auth/messages ---
add("Error", "Error", "Erreur")
add("Error", "Error", "Erreur")
add("Username doesn't exist", "Username doesn't exist", "Nom d'utilisateur n'existe pas")
add("Wrong password try again !", "Wrong password try again !", "Mot de passe incorrect, réessayez")

# --- Dialog title strings ---
add("Success", "Success", "Succès")
add("Warning", "Warning", "Avertissement")
add("Info", "Info", "Info")
add("No Selection", "No Selection", "Aucune sélection")
add("RNA Plugin", "RNA Plugin", "Plugin RNA")
add("RNA Plugin Error", "RNA Plugin Error", "Erreur du plugin RNA")
add("Select a file", "Select a file", "Sélectionnez un fichier")
add("Failed to Map layer.", "Failed to Map layer.", "Échec de la cartographie de la couche")
add("Please select a map layer option.", "Please select a map layer option.", "Veuillez sélectionner une option de couche cartographique")
add("No layer found with the name", "No layer found with the name", "Aucune couche trouvée avec le nom")
add("Edit stopped for layer", "Edit stopped for layer", "Édition arrêtée pour la couche")
add("Cannot stop editing for layer", "Cannot stop editing for layer", "Impossible d'arrêter l'édition pour la couche")
add("No active vector layer to save changes.", "No active vector layer to save changes.", "Aucune couche vectorielle active pour enregistrer les modifications")
add("Modification cancelled", "Modification cancelled", "Modification annulée")
add("Geometry outside your allowed area.", "Geometry outside your allowed area.", "Géométrie en dehors de votre zone autorisée")
add("Layer is not in edit mode.", "Layer is not in edit mode.", "La couche n'est pas en mode édition")
add("Changes saved successfully.", "Changes saved successfully.", "Modifications enregistrées avec succès")
add("Failed to save changes.", "Failed to save changes.", "Échec de l'enregistrement des modifications")
add("No active vector layer.", "No active vector layer.", "Aucune couche vectorielle active")
add("Unsupported geometry type.", "Unsupported geometry type.", "Type de géométrie non pris en charge")
add("Capture Point activated for selected vector layer.", "Capture Point activated for selected vector layer.", "Capture Point activé pour la couche vectorielle sélectionnée")
add("Capture Line activated for selected vector layer.", "Capture Line activated for selected vector layer.", "Capture Line activé pour la couche vectorielle sélectionnée")
add("Capture Polygon activated for selected vector layer.", "Capture Polygon activated for selected vector layer.", "Capture Polygon activé pour la couche vectorielle sélectionnée")
add("Select SQLite/SpatiaLite File", "Select SQLite/SpatiaLite File", "Sélectionnez un fichier SQLite/SpatiaLite")
add("Save Copy As", "Save Copy As", "Enregistrer la copie sous")
add("Dialog", "Dialog", "Dialogue")
add("Failed to create dialog", "Failed to create dialog", "Échec de la création du dialogue")
add("Check the QGIS log for details.", "Check the QGIS log for details.", "Consultez le journal QGIS pour plus de détails")

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

def _build_ar(translations: dict[str, str]) -> dict[str, str]:
    return {k: k for k in translations}

write_ts("en", EN, "i18n/RNA_en.ts")
write_ts("fr", FR, "i18n/RNA_fr.ts")
write_ts("ar", _build_ar(EN), "i18n/RNA_ar.ts")
print("Done!")
