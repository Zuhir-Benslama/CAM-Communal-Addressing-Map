"""Rename French-origin widget/variable names to English across the codebase.

Renames are applied to: .py, .ui, .json, .qml files.
Database column names (etat, situation, wilaya, commune) are NOT renamed.
"""
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# French→English rename pairs (longest first)
RENAMES = [
    ('on_select_catOrg', 'on_select_org_cat'),
    ('on_select_catAct', 'on_select_activity_cat'),
    ('fill_type_zone', 'fill_zone_type'),
    ('fill_type_city', 'fill_subd_type'),
    ('fill_type_org', 'fill_org_type'),
    ('fill_type_act', 'fill_activity_type'),
    ('type_act_3', 'activity_type_3'),
    ('type_voie', 'type_road'),
    ('nom_voie', 'road_name'),
    ('dec_voie', 'road_decision'),
    ('type_zone', 'zone_type'),
    ('type_city', 'subd_type'),
    ('cat_org', 'org_cat'),
    ('type_org', 'org_type'),
    ('cat_act', 'activity_cat'),
    ('type_act', 'activity_type'),
    ('submit_voie', 'submit_road'),
    ('submit_city', 'submit_subd'),
    ('num_etat', 'num_state'),
    ('etat_mont', 'mount_status'),
    ('list_voie', 'list_roads'),
    ('list_org', 'list_orgs'),
    ('list_cities', 'list_subds'),
    ('list_num', 'list_nums'),
    ('list_pan', 'list_panels'),
    ('dyn_ref', 'road_ref'),
    ('dyn_ref2', 'panel_ref'),
    ('select_ref', 'select_road_ref'),
    ('select_ref2', 'select_panel_ref'),
    ('page_num', 'page_numbering'),
    ('page_pan', 'page_panels'),
    ('nom_org', 'org_name'),
    ('nom_city', 'subd_name'),
]

# File extensions to process
INCLUDE_EXT = {'.py', '.ui', '.json', '.qml'}
# Directories to exclude
EXCLUDE_DIRS = {'.git', '__pycache__', '.mypy_cache', '.pytest_cache'}


def should_process_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in INCLUDE_EXT:
        return False
    for part in filepath.split(os.sep):
        if part in EXCLUDE_DIRS:
            return False
    return True


def apply_renames(filepath, changes):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Sort by length descending to avoid partial matches
    sorted_renames = sorted(RENAMES, key=lambda x: -len(x[0]))
    for old, new in sorted_renames:
        if old == new:
            continue
        # Replace as whole words (preceded/followed by non-alphanumeric or boundary)
        # We use a pattern that matches old surrounded by non-identifier chars
        content = re.sub(
            rf'(?<=[^a-zA-Z0-9_]){re.escape(old)}(?=[^a-zA-Z0-9_])',
            new, content,
        )
        # Also match at start of string
        content = re.sub(
            rf'^{re.escape(old)}(?=[^a-zA-Z0-9_])',
            new, content,
        )
        # Also match at end of string
        content = re.sub(
            rf'(?<=[^a-zA-Z0-9_]){re.escape(old)}$',
            new, content,
        )

    if content != original:
        changes.append(filepath)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    all_changes = []

    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            fpath = os.path.join(root, fname)
            if should_process_file(fpath):
                apply_renames(fpath, all_changes)

    print(f"Modified {len(all_changes)} files:")
    for f in sorted(all_changes):
        # Show relative path
        rel = os.path.relpath(f, REPO)
        print(f"  {rel}")

    # Quick verification
    print("\nVerification: checking for remaining French names...")
    remaining = {old for old, _ in RENAMES if old != 'submit_zone'}
    found = set()
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            fpath = os.path.join(root, fname)
            if should_process_file(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                for name in remaining:
                    # Check as whole word
                    if re.search(rf'(?<=[^a-zA-Z0-9_]){re.escape(name)}(?=[^a-zA-Z0-9_])', content):
                        found.add(name)

    if found:
        print(f"WARNING: {len(found)} names still found: {sorted(found)}")
    else:
        print("All renames verified successfully!")


if __name__ == '__main__':
    main()
