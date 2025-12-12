frappe.ui.form.on("Production Plan", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(
                "Material Transfer",
                function () {
                    frm.call("create_material_transfer").then(r => {
                        if (r.message) {
                            frappe.set_route("Form", "Stock Entry", r.message);
                        }
                    });
                },
                __("Create")
            );
        }
    }
});
