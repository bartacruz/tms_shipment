/** @odoo-module */

import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState,useRef } from "@odoo/owl";
import { KeepLast } from "@web/core/utils/concurrency";
import { fuzzyLookup } from "@web/core/utils/search";
import { Pager } from "@web/core/pager/pager";

export class DriverList extends Component {
    static components = { Pager };
    static template = "tms_shipment.DriverList";
    static props = {
        selectDriver: {
            type: Function,
        },
    };

    setup() {
        this.orm = useService("orm");
        this.partners = useState({ data: [] });
        this.pager = useState({ offset: 0, limit: 20 });
        this.keepLast = new KeepLast();
        this.state = useState({
            searchString: "",
            displayActiveDrivers: false,
        })

        onWillStart(async () => {
            const { length, records } = await this.loadDrivers();
            this.partners.data = records;
            this.pager.total = length;
        })
        this.onDrag = function(ev){
            console.debug("onDrag",this,ev);
            const driver_id = ev.srcElement.dataset.driverId;
            ev.dataTransfer.setData("text",driver_id);
            ev.dataTransfer.dropEffect = "move";
            ev.dataTransfer.effectAllowed = "move";
            console.debug("driver",driver_id);
        }
        this.onDrop = function(ev){
            console.debug("onDrop drivers",this,ev);
        }
        // this.env.bus.addEventListener('updatesss',this.loadDrivers.bind(this));
    }

    get displayedPartners() {
        return this.filterDrivers(this.state.searchString);
    }

    async onChangeActiveDrivers(ev) {
        this.state.displayActiveDrivers = ev.target.checked;
        this.partners.data = await this.keepLast.add(this.loadDrivers());
        this.pager.offset = 0;
        const { length, records } = await this.keepLast.add(this.loadDrivers());
        this.partners.data = records;
        this.pager.total = length;
    }

    filterDrivers(name) {
        if (name) {
            return fuzzyLookup(name, this.partners.data, (partner) => partner.display_name);
        } else {
            return this.partners.data;
        }
    }

    loadDrivers() {
        console.debug("loading drivers");
        const { limit, offset } = this.pager;
        const domain = this.state.displayActiveDrivers ? [["is_active", "!=", false]] : [];
        return this.orm.webSearchRead("tms.driver", domain, {
            specification: {
                "display_name": {},
            },
            limit,
            offset,
        })
    }


    async onUpdatePager(newState) {
        Object.assign(this.pager, newState);
        const { records } = await this.loadDrivers();
        this.partners.data = records;
        this.filterDrivers(this.filterName);
    }
}