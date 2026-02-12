/** @odoo-module **/

import { registry } from "@web/core/registry";

export class TMSService {
    /**
     * @param {import("@web/env").OdooEnv} env
     * @param {Partial<import("services").Services>} services
     */
    constructor(env, services) {
        this.busService = services.bus_service;
        this.env = env;
    }
    setup() {
        this.busService.addChannel("tms");
        this.busService.subscribe("order_changed",(notif) => {
            this.env.bus.trigger("order_changed", notif);
        });
        this.busService.subscribe("driver_changed",(notif) => {
            this.env.bus.trigger("driver_changed", notif);
        });
    }
}
export const tmsService = {
    dependencies: ["bus_service"],
    start(env, services) {
        const tmsService =  new TMSService(env, services);
        tmsService.setup();
        return tmsService;
    },
};

registry.category("services").add("tms_service", tmsService);

