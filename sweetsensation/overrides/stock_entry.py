import frappe

def override_difference_account(doc, method):
    if doc.stock_entry_type == "Manufacture":
        for item in doc.items:
            item.expense_account = "522116 - Stock Adjustment - SSC"