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
        this.action = useService("action");
        this.partners = useState({ data: [] });
        this.root = useRef('root');
        this.pager = useState({ offset: 0, limit: 15 });
        this.keepLast = new KeepLast();
        this.state = useState({
            searchString: "",
            displayActiveDrivers: false,
            lastSearch: "",
            folded:false,
        })
        this.busService = this.env.services.bus_service;
        this.busService.addChannel("drivers");
        this.busService.addEventListener('driver_changed', (a) => {
            //this.loadDrivers.bind(this);
            console.debug("driver_Changed",a);
        });
        this.busService.start();

        onWillStart(async () => {
            await this.updateDrivers();
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
        // this.env.bus.addEventListener('driver_changed', (a) => {
        //     console.debug("driver_Changed",a);
        // });
        console.debug("env:",this.env.services,this.root);
    }
    async selectDriver(ev) {
        console.debug("selectDriver",this,ev);
        const td = $(ev.srcElement).closest('.driver');
        const driver_id = td.data("driverId");
        console.debug("driverId",driver_id);
        
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Chofer',
            target: 'current',
            res_id: driver_id,
            res_model: 'tms.driver',
            views: [[false, 'form']],
        });
    }
    get displayedPartners() {
        // return this.filterDrivers(this.state.searchString);
        console.debug("getdisplayedPartners",this.state.searchString,this.state.lastSearch);
        if (this.state.searchString != this.state.lastSearch) {
            this.updateDrivers();
        }
        return this.partners.data;
    }

    async updateDrivers() {
        const { length, records } = await this.loadDrivers();
        this.partners.data = records;
        this.pager.total = length;
    }

    async onChangeActiveDrivers(ev) {
        this.state.displayActiveDrivers = ev.target.checked;
        this.updateDrivers();
        // this.partners.data = await this.keepLast.add(this.loadDrivers());
        // this.pager.offset = 0;
        // const { length, records } = await this.keepLast.add(this.loadDrivers());
        // this.partners.data = records;
        // this.pager.total = length;
    }
    
    filterDrivers(name) {
        console.debug("filterDrivers",name);
        if (name) {
            return fuzzyLookup(name, this.partners.data, (partner) => partner.display_name);
        } else {
            return this.partners.data;
        }
    }

    loadDrivers() {
        const { limit, offset } = this.pager;
        const domain = this.state.displayActiveDrivers ? [["stage_id", "in", [5] ]] : [];
        if (this.state.searchString.length > 2) {
            domain.push(['name','ilike',this.state.searchString]);
        }
        this.state.lastSearch = this.state.searchString;
        console.debug("loading drivers", domain);
        
        return this.orm.webSearchRead("tms.driver", domain, {
            specification: {
                "display_name": {},
                "stage_id": { fields: { name: {} } },
            },
            limit,
            offset,
        })
    }


    async onUpdatePager(newState) {
        Object.assign(this.pager, newState);
        const { records } = await this.loadDrivers();
        this.partners.data = records;
        // this.filterDrivers(this.filterName);
    }
}