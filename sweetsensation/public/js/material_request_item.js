// frappe.ui.form.on("Material Request Item", {
//     item_code(frm, cdt, cdn) {
//         const row = locals[cdt][cdn];

//         if (!row.item_code || !frm.doc.custom_item_group) return;

//         frappe.db.get_value("Item", row.item_code, "item_group").then(r => {
//             if (!r || r.message.item_group !== frm.doc.custom_item_group) {
//                 frappe.model.set_value(cdt, cdn, "item_code", "");
//                 frappe.msgprint("This item does not belong to the selected Item Group. Removed.");
//             }
//         });
//     }
// });
