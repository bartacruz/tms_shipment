odoo.define('tms_shipment.tms_order_list', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');

    var TMSOrderListWidget = AbstractField.extend({
        template: 'TMSOrderListWidgetTemplate', // Define a QWeb template for rendering

        // Add any custom events or methods for interaction
        events: {
            'click .o_tms_order_item': '_onItemClick',
        },

        _render: function () {
            // Logic to render the Many2many records based on your custom design
            // You can access the field's value through this.value
            // Example: Render a list of items
            this.$el.html(QWeb.render(this.template, {
                records: this.value.res_ids, // Assuming you want to display record IDs
                // You might need to fetch record data based on res_ids
            }));
        },

        _onItemClick: function (ev) {
            // Handle click events on your custom items
            var recordId = $(ev.currentTarget).data('record-id');
            // Perform actions like opening the record's form view
        },

        // Add other methods as needed for interacting with the Many2many field
    });
    var myWidget = 
    fieldRegistry.add('tms_order_list', TMSOrderListWidget);

    return TMSOrderListWidget;
});