frappe.ui.form.on('Item', {
    refresh: function(frm) {
        // Calculate volume when packaging details are updated
        frm.fields_dict['custom_item_packaging_details'].grid.get_field('length').$input.on('change', function() {
            calculate_volume(frm);
        });
        frm.fields_dict['custom_item_packaging_details'].grid.get_field('width').$input.on('change', function() {
            calculate_volume(frm);
        });
        frm.fields_dict['custom_item_packaging_details'].grid.get_field('height').$input.on('change', function() {
            calculate_volume(frm);
        });
    }
});

frappe.ui.form.on('Item Packaging Level Details', {
    length: function(frm, cdt, cdn) {
        calculate_row_volume(frm, cdt, cdn);
    },
    width: function(frm, cdt, cdn) {
        calculate_row_volume(frm, cdt, cdn);
    },
    height: function(frm, cdt, cdn) {
        calculate_row_volume(frm, cdt, cdn);
    }
});

function calculate_row_volume(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let length = parseFloat(row.length) || 0;
    let width = parseFloat(row.width) || 0;
    let height = parseFloat(row.height) || 0;
    
    let volume = length * width * height;
    
    frappe.model.set_value(cdt, cdn, 'volume', volume);
}

function calculate_volume(frm) {
    let packaging_details = frm.doc.custom_item_packaging_details || [];
    
    packaging_details.forEach(function(row) {
        let length = parseFloat(row.length) || 0;
        let width = parseFloat(row.width) || 0;
        let height = parseFloat(row.height) || 0;
        
        let volume = length * width * height;
        
        if (row.volume !== volume) {
            frappe.model.set_value(row.doctype, row.name, 'volume', volume);
        }
    });
}