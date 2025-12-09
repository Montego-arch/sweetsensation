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




import frappe

# -----------------------------
# Helper Functions
# -----------------------------

def find_warehouse(branch, pattern):
    """Return a single warehouse matching custom_branch + name like pattern."""
    return frappe.get_all(
        "Warehouse",
        fields=["name"],
        filters=[
            ["custom_branch", "=", branch],
            ["LOWER(name)", "like", f"%{pattern.lower()}%"]
        ],
        limit=1
    )

def check_unique_warehouse(doc, keyword, error_message):
    """Ensure only ONE warehouse of each type exists per branch."""
    exists = frappe.db.sql("""
        SELECT name 
        FROM `tabWarehouse`
        WHERE custom_branch = %s
          AND LOWER(name) LIKE %s
          AND name != %s
        LIMIT 1
    """, (doc.custom_branch, f"%{keyword.lower()}%", doc.name))

    if exists:
        frappe.throw(error_message)


# -----------------------------
# EVENT: Warehouse Before Save
# -----------------------------

def validate_warehouse_rules(doc, method=None):
    """Warehouse uniqueness + branch-level restrictions."""

    warehouse_lower = doc.warehouse_name.lower()

    # ---- Unique Outlet Rule ----
    if "outlet" in warehouse_lower:
        check_unique_warehouse(
            doc,
            "outlet",
            "An outlet already exists for this branch. Branches must have only ONE outlet warehouse."
        )

    # ---- Unique Transit Warehouse ----
    if "transit" in warehouse_lower:
        check_unique_warehouse(
            doc,
            "transit",
            "A transit warehouse already exists for this branch. Branches must have only ONE transit warehouse."
        )

    # ---- Unique Restaurant ----
    if "restaurant" in warehouse_lower:
        check_unique_warehouse(
            doc,
            "restaurant",
            "A restaurant already exists for this branch. Only ONE restaurant per branch is allowed."
        )

    # No field assignment is required here — this is only validation.
    # Done.


# -----------------------------
# EVENT: Work Order Before Insert
# -----------------------------

def assign_work_order_warehouses(doc, method=None):
    """
    Sets warehouses for Work Order created from Production Plan:
      - Source: Warehouse containing 'production'
      - Target: Warehouse containing 'restaurant'
    """

    if not doc.custom_branch:
        return

    # Find source warehouse (Production)
    source = find_warehouse(doc.custom_branch, "production")

    if not source:
        frappe.throw("Branch on Production Plan is not linked to any Production warehouse.")

    # Find target warehouse (Restaurant)
    target = find_warehouse(doc.custom_branch, "restaurant")

    if not target:
        frappe.throw("Branch on Production Plan is not linked to any Restaurant warehouse.")

    source_wh = source[0].name
    target_wh = target[0].name

    # Assign to Work Order
    doc.source_warehouse = source_wh
    doc.fg_warehouse = target_wh  # Finished goods / target warehouse

    # Assign source warehouse to required items table
    if source_wh:
        for row in doc.required_items:
            row.source_warehouse = source_wh
