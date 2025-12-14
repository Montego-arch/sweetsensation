import frappe
from frappe.model.document import Document

class CustomProductionPlan(Document):

    @frappe.whitelist()
    def create_material_transfer(self):
        if not self.mr_items:
            frappe.throw("No raw materials found in this Production Plan.")

        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Transfer"
        se.company = self.company

        # optional: set default source & target warehouses
        # default_source = frappe.db.get_single_value("Stock Settings", "default_warehouse")
        # default_target = frappe.db.get_single_value("Stock Settings", "default_target_warehouse")

        for rm in self.mr_items:   # Production Plan Raw Materials table
            se.append("mr_items", {
                "item_code": rm.item_code,
                "qty": rm.required_qty or rm.quantity or 0,
                "uom": rm.uom,
                "stock_uom": rm.stock_uom or rm.uom,
                # "s_warehouse": default_source,
                # "t_warehouse": default_target
            })

        se.save(ignore_permissions=True)
        frappe.db.commit()

        return se.name
