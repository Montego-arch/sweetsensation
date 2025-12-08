# SERVER SCRIPT: ENFORCE ITEM GROUP MATCHING
import frappe


def validate_item_groups(doc, method):
    if not doc.custom_item_group:
        frappe.throw("Please select an Item Group before adding items.")

    for row in doc.items:
        if not row.item_code:
            continue

        item_group = frappe.db.get_value("Item", row.item_code, "item_group")

        if item_group != doc.custom_item_group:
            frappe.throw(
                f"Item <b>{row.item_code}</b> belongs to Item Group <b>{item_group}</b>, "
                f"but the selected Item Group is <b>{doc.custom_item_group}</b>."
            )


# CLEAR ITEMS IF ITEM GROUP CHANGES
def clear_on_group_change(doc, method):
    # Only clear if the doc is not new
    if not doc.is_new():
        previous_group = frappe.db.get_value("Material Request", doc.name, "custom_item_group")
        if previous_group and previous_group != doc.custom_item_group:
            doc.items = []



def get_branch_warehouses(branch):
    """Return warehouses linked to the given custom_branch."""
    return frappe.get_all(
        "Warehouse",
        filters={"custom_branch": branch},
        fields=["name"]
    )

def assign_warehouses(doc, method=None):
    branch = None

    # Get Production Plan's custom_branch
    if doc.production_plan:
        branch = frappe.db.get_value("Production Plan", doc.production_plan, "custom_branch")

    if not branch:
        return

    warehouses = get_branch_warehouses(branch)

    source_wh = None
    target_wh = None

    for wh in warehouses:
        wh_lower = wh.name.lower()

        # Source Warehouse rule
        if "store" in wh_lower:
            source_wh = wh.name

        # Target Warehouse rule
        if any(x in wh_lower for x in ["restaurant", "factory", "lounge"]):
            target_wh = wh.name

    # Apply to Work Order
    if source_wh:
        doc.source_warehouse = source_wh

    if target_wh:
        doc.fg_warehouse = target_wh 

def validate(doc, method):
    assign_warehouses(doc)
