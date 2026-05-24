"""Transform RNA_dialog_base.ui: consolidate 6 operational tabs into 1.

The 6 entity-specific tabs (Zones, Roads, Facilities, Subdivisions,
Numbering, Panels) each had an identical 3-button toolbar (draw/select/edit).
This script keeps only the first as the unified 'Operations' tab, adds
a layer selector dropdown + shared toolbar + QStackedWidget with 6 form pages,
and removes the other 5 operational tabs.
"""

import xml.etree.ElementTree as ET
import copy

UI_PATH = "gui/RNA_dialog_base.ui"

NS = "{http://www.w3.org/XML/1998/namespace}"
NSMAP = {"xml": NS}


def _find_text(elem, path):
    """Find text content at a relative XPath-like path."""
    parts = path.split("/")
    current = elem
    for part in parts:
        found = False
        for child in current:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == part:
                current = child
                found = True
                break
        if not found:
            return ""
    return current.text or ""


def _make_element(tag, attrib=None, text=None):
    """Create a new Element."""
    e = ET.Element(tag, attrib or {})
    if text is not None:
        e.text = text
    return e


def _make_sub(parent, tag, attrib=None, text=None):
    """Create a sub-element with optional text."""
    e = ET.SubElement(parent, tag, attrib or {})
    if text is not None:
        e.text = text
    return e


def _indent(elem, level=0):
    """Add whitespace indentation to the XML tree."""
    indent = "\n" + level * "  "
    child = None
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            _indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent


def transform():
    tree = ET.parse(UI_PATH)
    root = tree.getroot()

    for tab_widget in root.iter("widget"):
        if tab_widget.get("class") == "QTabWidget" and tab_widget.get("name") == "menu":
            _process_menu(tab_widget)
            break

    _indent(root)
    tree.write(UI_PATH, xml_declaration=True, encoding="utf-8")
    print("✓ UI tab consolidation complete.")


def _process_menu(menu):
    # Get all tab pages (child widget elements)
    pages = list(menu.findall("widget"))
    if len(pages) < 8:
        print(f"Warning: expected 8 tabs, found {len(pages)}")
        return

    op_pages = pages[:6]  # tabs 0-5: operational
    pages[6:]  # tabs 6-7: Report, Settings

    # Layer names in order matching the tabs
    layer_keys = ["zone", "road", "org", "city", "num", "pan"]
    layer_labels = ["Zones", "Roads", "Facilities", "Subdivisions", "Numbering", "Panels"]

    # For each operational page, extract the form content (everything after
    # the first toolbar frame) and the submit/list buttons
    form_contents = []
    submit_names = []
    extra_buttons = []

    for i, page in enumerate(op_pages):
        content = _extract_form_and_buttons(page)
        if content:
            form_contents.append(content["form"])
            submit_names.append(content.get("submit_name", ""))
            extra_buttons.append(content.get("extra_buttons", []))
        else:
            form_contents.append(None)
            submit_names.append("")
            extra_buttons.append([])

    # Remove all operational pages from the menu
    for page in op_pages:
        menu.remove(page)

    # --- Build the unified Operations tab ---
    ops_page = ET.Element("widget", {"class": "QWidget", "name": "tab_ops"})

    title_attr = ET.SubElement(ops_page, "attribute", {"name": "title"})
    ET.SubElement(title_attr, "string").text = "Operations"

    # Main vertical layout
    main_layout = ET.SubElement(ops_page, "layout",
                                {"class": "QVBoxLayout", "name": "verticalLayout_ops"})

    # --- Row 1: Layer selector ---
    sel_item = ET.SubElement(main_layout, "item")
    sel_combo = ET.SubElement(sel_item, "widget",
                              {"class": "QComboBox", "name": "layer_selector"})
    for label in layer_labels:
        item_el = ET.SubElement(sel_combo, "item")
        prop = ET.SubElement(item_el, "property", {"name": "text"})
        ET.SubElement(prop, "string").text = label

    # --- Row 2: Shared toolbar ---
    tb_item = ET.SubElement(main_layout, "item")
    tb_frame = ET.SubElement(tb_item, "widget",
                             {"class": "QFrame", "name": "toolbar_frame"})
    ET.SubElement(tb_frame, "property", {"name": "frameShape"})
    # Placeholder: no special frame shape

    tb_layout = ET.SubElement(tb_frame, "layout",
                              {"class": "QHBoxLayout", "name": "toolbar_layout"})

    btn_specs = [
        ("draw_btn", "Draw", "draw"),
        ("select_btn", "Select", "select"),
        ("edit_btn", "Edit", "edit"),
    ]
    for bname, btext, _ in btn_specs:
        btn_item = ET.SubElement(tb_layout, "item")
        btn = ET.SubElement(btn_item, "widget",
                            {"class": "QPushButton", "name": bname})
        minsize = ET.SubElement(btn, "property", {"name": "minimumSize"})
        sz = ET.SubElement(minsize, "size")
        ET.SubElement(sz, "width").text = "100"
        ET.SubElement(sz, "height").text = "0"
        font_prop = ET.SubElement(btn, "property", {"name": "font"})
        font_el = ET.SubElement(font_prop, "font")
        ET.SubElement(font_el, "weight").text = "75"
        ET.SubElement(font_el, "bold").text = "true"
        text_prop = ET.SubElement(btn, "property", {"name": "text"})
        ET.SubElement(text_prop, "string").text = btext

    # --- Row 3: QStackedWidget with 6 form pages ---
    stack_item = ET.SubElement(main_layout, "item")
    stack = ET.SubElement(stack_item, "widget",
                          {"class": "QStackedWidget", "name": "form_stack"})

    for i, key in enumerate(layer_keys):
        page_el = ET.SubElement(stack, "widget",
                                {"class": "QWidget", "name": f"page_{key}"})

        # Add form content from original tab
        if form_contents[i] is not None:
            page_el.append(form_contents[i])

    # --- Row 4: Spacer ---
    sp_item = ET.SubElement(main_layout, "item")
    sp = ET.SubElement(sp_item, "spacer", {"name": "verticalSpacer_ops"})
    ET.SubElement(sp, "property", {"name": "orientation"})
    enum_el = ET.SubElement(ET.SubElement(sp, "property",
                                          {"name": "orientation"}), "enum")
    enum_el.text = "Qt::Vertical"

    # Insert the ops page as the first tab
    menu.insert(0, ops_page)

    # Update currentIndex
    for prop in menu.findall("property"):
        if prop.get("name") == "currentIndex":
            num = prop.find("number")
            if num is not None:
                num.text = "0"

    print("Unified Operations tab created. Remaining tabs:")
    for i, p in enumerate(menu.findall("widget")):
        title = _find_text(p, "attribute/string")
        print(f"  {i}. {p.get('name')} = {title}")


def _is_toolbar_frame(frame_elem):
    """Check if a QFrame element contains draw/select/edit buttons."""
    for widget in frame_elem.iter("widget"):
        if widget.get("class") == "QPushButton":
            name = widget.get("name", "")
            if name.startswith("draw_") or name.startswith("select_") or name.startswith("edit_"):
                return True
    return False


def _remove_toolbar_items(layout_elem):
    """Remove toolbar items from a layout element in-place."""
    to_remove = []
    for item in layout_elem.findall("item"):
        for widget in item.findall("widget"):
            if widget.get("class") == "QFrame" and _is_toolbar_frame(widget):
                to_remove.append(item)
                break
    for item in to_remove:
        layout_elem.remove(item)
    return layout_elem


def _extract_form_and_buttons(page):
    """Extract form content from a tab page, removing toolbar frames."""
    # The structure is: page > layout > item > QWidget container > inner_layout > items
    layout = page.find("layout")
    if layout is None:
        return None

    # Find the container widget and its inner layout
    for item in layout.findall("item"):
        for container in item.findall("widget"):
            if container.get("class") in ("QWidget",) and container.get("name", "").startswith("widget_"):
                inner_layout = container.find("layout")
                if inner_layout is not None:
                    # Remove toolbar items from the inner layout
                    cleaned = _remove_toolbar_items(copy.deepcopy(inner_layout))
                    return {"form": cleaned, "submit_name": "", "extra_buttons": []}

    # Fallback: use the top-level layout items minus toolbar
    form_layout = ET.Element("layout",
                             {"class": "QVBoxLayout",
                              "name": f"form_{page.get('name', 'unknown')}"})
    for item in layout.findall("item"):
        skip = False
        for widget in item.findall("widget"):
            if widget.get("class") == "QFrame" and _is_toolbar_frame(widget):
                skip = True
                break
        if not skip:
            form_layout.append(copy.deepcopy(item))
    return {"form": form_layout, "submit_name": "", "extra_buttons": []}


if __name__ == "__main__":
    transform()
