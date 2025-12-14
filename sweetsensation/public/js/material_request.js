
// // MATERIAL REQUEST FORM SCRIPT
// frappe.ui.form.on("Material Request", {
//     refresh(frm) {
//         set_item_filter(frm);
//     },

//     custom_item_group(frm) {
//         clear_items_on_group_change(frm);
//         set_item_filter(frm);
//     },

//     validate(frm) {
//         enforce_validation(frm);
//     }
// });


// // ----------------------------------------------------------------
// // FILTER ITEM DROPDOWN BY ITEM GROUP
// // ----------------------------------------------------------------
// function set_item_filter(frm) {
//     frm.fields_dict["items"].grid.get_field("item_code").get_query = function() {
//         return {
//             query: "erpnext.controllers.queries.item_query",
//             filters: {
//                 item_group: frm.doc.custom_item_group || ""
//             }
//         };
//     };
// }


// // ----------------------------------------------------------------
// // CLEAR ITEM TABLE WHEN ITEM GROUP CHANGES
// // ----------------------------------------------------------------
// function clear_items_on_group_change(frm) {
//     frm.clear_table("items");
//     frm.refresh_field("items");
//     frappe.msgprint("All items have been cleared because Item Group was changed.");
// }


// // ----------------------------------------------------------------
// // VALIDATE MATCHING ITEM GROUPS BEFORE SAVE (FULL BLOCKER)
// // ----------------------------------------------------------------
// function enforce_validation(frm) {
//     const parent_group = frm.doc.custom_item_group;

//     if (!parent_group) {
//         frappe.throw("Please select an Item Group before adding items.");
//     }

//     (frm.doc.items || []).forEach(row => {
//         if (!row.item_code) return;

//         // IMPORTANT: USE SYNC DATABASE CALL 
//         let result = frappe.db.get_value_sync("Item", row.item_code, "item_group");

//         if (!result) return;

//         if (result.item_group !== parent_group) {
//             frappe.throw(
//                 `Item <b>${row.item_code}</b> belongs to <b>${result.item_group}</b>, 
//                 but the selected Item Group is <b>${parent_group}</b>.`
//             );
//         }
//     });
// }


// // ----------------------------------------------------------------
// // AUTO-CLEAR ITEM IMMEDIATELY WHEN SELECTED IF WRONG GROUP
// // ----------------------------------------------------------------
// frappe.ui.form.on("Material Request Item", {
//     item_code(frm, cdt, cdn) {
//         const row = locals[cdt][cdn];

//         if (!row.item_code || !frm.doc.custom_item_group) return;

//         let result = frappe.db.get_value_sync("Item", row.item_code, "item_group");

//         if (result && result.item_group !== frm.doc.custom_item_group) {
//             frappe.model.set_value(cdt, cdn, "item_code", "");
//             frappe.msgprint(
//                 `This item does NOT belong to Item Group <b>${frm.doc.custom_item_group}</b>. It has been removed.`
//             );
//         }
//     }
// });


