/** @odoo-module  */

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { DriverList } from "./driver_list";

export class TMSKanbanController extends KanbanController {
    static components = { ...KanbanController.components, DriverList}
    static template = "tms_shipment.TMSKanbanController";

    setup() {
        super.setup();
        this.searchKey = Symbol("isFromTmsKanban");
    }

    selectDriver(partner_id, partner_name) {
        const driverFilters = this.env.searchModel.getSearchItems((searchItem) =>
            searchItem[this.searchKey]
        );
        for (const driverFilter of driverFilters) {
            if (driverFilter.isActive) {
                this.env.searchModel.toggleSearchItem(driverFilter.id);
            }
        }
        this.env.searchModel.createNewFilters([{
            description: partner_name,
            domain: [["partner_id", "=", partner_id]],
            [this.searchKey]: true,
        }])
    }
}