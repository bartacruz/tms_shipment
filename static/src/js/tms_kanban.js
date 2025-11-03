/** @odoo-module */

import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { TMSKanbanController } from "./kanban_controller";

const tmsKanbanController = {
    ...kanbanView,
    Controller: TMSKanbanController,
};

registry.category("views").add("tms_kanban", tmsKanbanController);