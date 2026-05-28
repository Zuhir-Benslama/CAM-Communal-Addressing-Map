#!/usr/bin/env python3
"""Migrate an old RNA database to the current schema.

Usage:
    python scripts/migrate_db.py /path/to/old.sqlite /path/to/output.sqlite
"""
import sys
import os
import json
import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("migrate_db")


COLUMN_MAP = {
    "localite": {
        "pk_uid": "id",
        "wilaya": "wilaya",
        "codeWilaya": "wilaya_code",
        "communeAr": "commune_ar",
        "codeCommun": "commune_code",
        "geometry": "geometry",
    },
    "user": {
        "id": "id",
        "username": "username",
        "first_name": "first_name",
        "last_name": "last_name",
        "password": "password",
        "active": "active",
        "affectation_id": "affectation_id",
        "api_key": "api_key",
        "email": "email",
        "phone": "phone",
    },
    "refpoly": {
        "pkuid": "id",
        "idLoc": "locality_id",
        "Type": "Type",
        "Nom": "Nom",
        "geometry": "geometry",
        "has_child": "has_child",
        "uid": "user_id",
    },
    "refpolychild": {
        "pkuid": "id",
        "idLoc": "locality_id",
        "Type": "Type",
        "Nom": "Nom",
        "geometry": "geometry",
        "parent": "parent",
        "uid": "user_id",
    },
    "RefLine": {
        "pkuid": "id",
        "num_decision": "decision_number",
        "Type": "Type",
        "Nom": "Nom",
        "idLoc": "locality_id",
        "geometry": "geometry",
        "pkuid_poly": "zone_id",
        "uid": "user_id",
    },
    "reforg": {
        "pkuid": "id",
        "idLoc": "locality_id",
        "Type": "Type",
        "Cat": "category",
        "Nom": "Nom",
        "geometry": "geometry",
        "uid": "user_id",
        "pkuid_poly": "zone_id",
    },
    "Numerotation": {
        "pkuid": "id",
        "valeur": "valeur",
        "idLine": "road_id",
        "idPoly": "subdivision_id",
        "repetition": "repetition",
        "etat": "etat",
        "geometry": "geometry",
        "uid": "user_id",
        "activity_cat": "activity_cat",
        "activity_type": "activity_type",
    },
    "Pannautage": {
        "pkuid": "id",
        "dim": "dimensions",
        "Type": "Type",
        "Stituation": "situation",
        "idLine": "road_id",
        "idPoly": "subdivision_id",
        "idOrg": "organization_id",
        "geometry": "geometry",
        "uid": "user_id",
    },
}

LOOKUP_TABLES = [
    "DimPan", "Etat_Numerotation", "situation_Montage",
    "type_cite", "type_voie", "type_zone", "type_organisme", "activity",
]

NEW_TABLES = {
    "localite": """
        CREATE TABLE localite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wilaya TEXT NOT NULL,
            wilaya_code INTEGER NOT NULL,
            commune_ar TEXT NOT NULL,
            commune_fr TEXT,
            commune_en TEXT,
            commune_code TEXT NOT NULL,
            created_at DATETIME,
            updated_at DATETIME
        )
    """,
    "user": """
        CREATE TABLE user (
            id TEXT NOT NULL,
            username VARCHAR(255) NOT NULL,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            password VARCHAR(255),
            active BOOLEAN,
            affectation_id INTEGER,
            api_key TEXT,
            email VARCHAR(255),
            phone VARCHAR(255),
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            UNIQUE (username),
            FOREIGN KEY (affectation_id) REFERENCES localite(id)
        )
    """,
    "refpoly": """
        CREATE TABLE refpoly (
            id TEXT NOT NULL,
            locality_id VARCHAR,
            Type VARCHAR NOT NULL,
            Nom VARCHAR,
            Nom_fr TEXT,
            Nom_en TEXT,
            has_child BOOLEAN NOT NULL DEFAULT 0,
            user_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (locality_id) REFERENCES localite(id),
            FOREIGN KEY (Type) REFERENCES type_zone(pk),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
    "refpolychild": """
        CREATE TABLE refpolychild (
            id TEXT NOT NULL,
            locality_id VARCHAR,
            Type VARCHAR NOT NULL,
            Nom VARCHAR,
            Nom_fr TEXT,
            Nom_en TEXT,
            parent TEXT,
            user_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (locality_id) REFERENCES localite(id),
            FOREIGN KEY (Type) REFERENCES type_cite(pk),
            FOREIGN KEY (parent) REFERENCES refpoly(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
    "RefLine": """
        CREATE TABLE RefLine (
            id TEXT NOT NULL,
            decision_number TEXT,
            Type VARCHAR NOT NULL,
            Nom VARCHAR,
            Nom_fr TEXT,
            Nom_en TEXT,
            locality_id VARCHAR NOT NULL,
            zone_id TEXT,
            user_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (Type) REFERENCES type_voie(pk),
            FOREIGN KEY (locality_id) REFERENCES localite(id),
            FOREIGN KEY (zone_id) REFERENCES refpoly(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
    "reforg": """
        CREATE TABLE reforg (
            id TEXT NOT NULL,
            locality_id VARCHAR,
            Type VARCHAR,
            category VARCHAR,
            Nom VARCHAR,
            Nom_fr TEXT,
            Nom_en TEXT,
            user_id TEXT,
            zone_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (locality_id) REFERENCES localite(id),
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (zone_id) REFERENCES refpoly(id)
        )
    """,
    "Numerotation": """
        CREATE TABLE Numerotation (
            id TEXT NOT NULL,
            valeur TEXT NOT NULL,
            road_id TEXT,
            subdivision_id TEXT,
            repetition VARCHAR,
            etat VARCHAR,
            user_id TEXT,
            activity_cat VARCHAR,
            activity_type VARCHAR,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (road_id) REFERENCES RefLine(id),
            FOREIGN KEY (subdivision_id) REFERENCES refpolychild(id),
            FOREIGN KEY (etat) REFERENCES Etat_Numerotation(pk),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
    "Pannautage": """
        CREATE TABLE Pannautage (
            id TEXT NOT NULL,
            dimensions VARCHAR NOT NULL,
            Type TEXT,
            situation VARCHAR,
            road_id TEXT,
            subdivision_id TEXT,
            organization_id TEXT,
            user_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (dimensions) REFERENCES DimPan(pk),
            FOREIGN KEY (situation) REFERENCES situation_Montage(pk),
            FOREIGN KEY (road_id) REFERENCES RefLine(id),
            FOREIGN KEY (subdivision_id) REFERENCES refpolychild(id),
            FOREIGN KEY (organization_id) REFERENCES reforg(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
}

LOOKUP_TABLE_DDL = {
    "DimPan": "CREATE TABLE DimPan (pk VARCHAR NOT NULL PRIMARY KEY)",
    "Etat_Numerotation": "CREATE TABLE Etat_Numerotation (pk VARCHAR NOT NULL PRIMARY KEY)",
    "situation_Montage": "CREATE TABLE situation_Montage (pk VARCHAR NOT NULL PRIMARY KEY)",
    "type_cite": "CREATE TABLE type_cite (pk VARCHAR NOT NULL PRIMARY KEY)",
    "type_voie": "CREATE TABLE type_voie (pk VARCHAR NOT NULL PRIMARY KEY)",
    "type_zone": "CREATE TABLE type_zone (pk VARCHAR NOT NULL PRIMARY KEY)",
    "type_organisme": "CREATE TABLE type_organisme (pk VARCHAR NOT NULL, cat VARCHAR NOT NULL, PRIMARY KEY (pk, cat))",
    "activity": "CREATE TABLE activity (cat VARCHAR NOT NULL, type VARCHAR NOT NULL, PRIMARY KEY (cat, type))",
}


SPATIALITE_LIB = os.environ.get(
    "SPATIALITE_LIB",
    "/usr/libspatialite50/lib/mod_spatialite.so",
)


def init_spatialite(conn: sqlite3.Connection) -> None:
    """Initialize SpatiaLite metadata in the new database."""
    conn.enable_load_extension(True)
    conn.load_extension(SPATIALITE_LIB)
    conn.execute("SELECT InitSpatialMetadata(1)")


def register_geometry(
    conn: sqlite3.Connection, table: str, col: str,
    geom_type: str, srid: int = 4326, dims: int = 2,
) -> None:
    """Register a geometry column using AddGeometryColumn."""
    conn.execute(
        f"SELECT AddGeometryColumn('{table}', '{col}', {srid}, "
        f"'{geom_type}', {dims})"
    )


def create_spatial_index(conn: sqlite3.Connection, table: str, col: str) -> None:
    """Create a spatial R-tree index."""
    conn.execute(f"SELECT CreateSpatialIndex('{table}', '{col}')")


GEOMETRY_TYPES = {
    "localite": ("GEOMETRY", 4326, 2, 0),
    "refpoly": ("POLYGON", 4326, 2, 3),
    "refpolychild": ("POLYGON", 4326, 2, 3),
    "RefLine": ("LINESTRING", 4326, 2, 2),
    "reforg": ("POLYGON", 4326, 2, 3),
    "Numerotation": ("POINT", 4326, 2, 1),
    "Pannautage": ("POINT", 4326, 2, 1),
}


def migrate(old_path: str, new_path: str) -> None:
    """Migrate old database to new schema."""

    if os.path.exists(new_path):
        logger.error("Output file already exists: %s", new_path)
        sys.exit(1)

    old = sqlite3.connect(old_path)
    old.row_factory = sqlite3.Row
    new = sqlite3.connect(new_path)
    new.execute("PRAGMA foreign_keys = OFF")
    new.execute("PRAGMA journal_mode = WAL")

    logger.info("Initializing SpatiaLite metadata...")
    init_spatialite(new)

    logger.info("Creating lookup tables...")
    for name, ddl in LOOKUP_TABLE_DDL.items():
        new.execute(ddl)
        old_cur = old.execute(f"SELECT * FROM \"{name}\"")
        old_rows = old_cur.fetchall()
        if old_rows:
            cols = [desc[0] for desc in old_cur.description]
            placeholders = ",".join("?" for _ in cols)
            col_list = ",".join(f'"{c}"' for c in cols)
            for row in old_rows:
                new.execute(
                    f"INSERT INTO \"{name}\" ({col_list}) "
                    f"VALUES ({placeholders})",
                    tuple(row[c] for c in cols),
                )
            logger.info("  %s: %d rows", name, len(old_rows))
        else:
            logger.info("  %s: 0 rows (skipped)", name)

    logger.info("Creating spatial tables...")
    for table, ddl in NEW_TABLES.items():
        new.execute(ddl)
        logger.info("  Created %s", table)

    logger.info("Registering geometry columns...")
    for table, (geom_type, srid, dims, _geom_code) in GEOMETRY_TYPES.items():
        try:
            register_geometry(new, table, "geometry", geom_type, srid, dims)
        except Exception as e:
            logger.warning("  %s.geometry: %s", table, e)

    logger.info("Copying data...")
    for table, col_map in COLUMN_MAP.items():
        old_cols = list(col_map.keys())
        new_cols = list(col_map.values())

        old_rows = old.execute(
            f"SELECT * FROM \"{table}\""
        ).fetchall()
        if not old_rows:
            logger.info("  %s: 0 rows (skipped)", table)
            continue

        placeholders = ",".join("?" for _ in new_cols)
        new_col_list = ",".join(f'"{c}"' for c in new_cols)

        migrated = 0
        for row in old_rows:
            try:
                values = []
                for old_c in old_cols:
                    values.append(row[old_c])
                new.execute(
                    f"INSERT INTO \"{table}\" ({new_col_list}) "
                    f"VALUES ({placeholders})",
                    values,
                )
                migrated += 1
            except Exception as e:
                logger.warning(
                    "  %s row %s: %s", table, row.get("pkuid", row.get("id", "?")), e,
                )
        logger.info("  %s: %d / %d rows migrated", table, migrated, len(old_rows))

    new.commit()

    logger.info("Creating spatial indexes...")
    for table, _ in GEOMETRY_TYPES.items():
        try:
            create_spatial_index(new, table, "geometry")
            logger.info("  %s.geometry: index created", table)
        except Exception as e:
            logger.warning("  %s.geometry index: %s", table, e)

    new.execute("PRAGMA foreign_keys = ON")
    new.commit()
    new.close()
    old.close()
    logger.info("Migration complete: %s", new_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    migrate(sys.argv[1], sys.argv[2])
