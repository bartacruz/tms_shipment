/** @odoo-module **/

import { Component, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import {useX2ManyCrud} from "@web/views/fields/relational_utils";
import {useDebounced} from "@web/core/utils/timing";


export class TripsField extends Component {
    static template = "tms_shipment.TripsField";
    static props = {
        ...standardFieldProps,
    }
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        const { saveRecord, updateRecord, removeRecord } = useX2ManyCrud(
            () => this.props.record.data[this.props.name],
            false
        );
        this.refresh = useDebounced(this.refresh,1500);

        this.assignTrip = async (trip,driver) => {
            this.env.services.ui.block();
            const assigned = await this.orm.call('tms.order', "assign_driver", [trip,driver], {
                context: this.props.context,
            });
            console.debug("assigned",assigned, typeof(assigned));
            
            
            // const tripRecord = this.props.record.data[this.props.name].records.find(
            //     (record) => record.resId === assigned
            // );
            // tripRecord.dirty=true;
            // console.debug("assigned",assigned,tripRecord,tripRecord.isNew,tripRecord.dirty);
            // this.props.record.data[this.props.name].validateExtendedRecord(tripRecord);
            await this.refresh();
            
            this.env.services.ui.unblock();
            return assigned;
            // const trip2 = this.getTrip(tripRecord);
            // console.debug("assigned",assigned,tripRecord,trip2);
            
            
            // this.props.record.data[this.props.name].load();
        };
        const searchModel = this.env.searchModel;
        
    }
    async refresh() {
        await this.action.loadState();
        const controller = this.action.currentController
        const action = controller.action
        console.debug("action:",controller,action);
        this.action.doAction(action)
    }
    getTrip(record) {
        var driver = record.data.driver_id ? record.data.driver_id[1] : false;
        var vehicle = record.data.vehicle_id ? record.data.vehicle_id[1] : false;
        var trailer = record.data.trailer_id ? record.data.trailer_id[1] : false;
        let class_str = "o_trip m-1 p-2 ";
        
        if (!driver) {
            class_str = class_str + " text-bg-info";
        } else if (!vehicle) {
            class_str = class_str + " text-bg-warning";
        } else if (record.data.is_active) {
            class_str = class_str + " text-bg-primary";
        } else if (record.data.is_completed) {
            class_str = class_str + " text-bg-success";
        } 
        return {
            id: record.id, // datapoint_X
            resId: record.resId,
            text: record.data.display_name,
            colorIndex: record.data[this.props.colorField],
            driver: driver,
            vehicle: vehicle,
            trailer: trailer,
            is_active: record.data.is_active,
            is_completed: record.data.is_completed,
            class: class_str,
            save:(ev) => {
                console.debug("SAVE PEDORRO",this,ev);
            },
        };
        
    }
    async onClick(ev) {
        ev.stopPropagation();
        var target = $(ev.target).closest('.o_trip');
        const trip = target.data("id");
        console.debug("onclick",trip);
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Viaje',
            target: 'current',
            res_id: trip,
            res_model: 'tms.order',
            views: [[false, 'form']],
        });
    }
    async onDragEnter(ev) {
        var target = $(ev.target);
        target.closest('.o_trip').addClass('o_sarasa');
    }

    onDragLeave(ev) {
        var target = $(ev.target);
        target.closest('.o_trip').removeClass('o_sarasa');
    }
    onDrop(ev,a,b) {
        console.debug("onDrop Trip out", ev);
        var target = $(ev.target).closest('.o_trip');
        target.removeClass('o_sarasa');
        
        const driver_id = ev.dataTransfer.getData("text");
        const trip = target.data("id");
        console.debug("driver_id",driver_id,"trip",trip);
        this.assignTrip(trip,driver_id);

        // if (this.props.readonly) {
        //     return;
        // }
        // this.onTagKeydown(ev);
}
    get trips() {
        return this.props.record.data[this.props.name].records.map((record) =>
            this.getTrip(record)
        );
    }
}
export const tripsField = {
    component: TripsField,
    displayName:"Trips",
    supportedTypes: ["many2many"],
    relatedFields: (fieldInfo) => {
        return [ {name:'id', type:"int"},{ name: "display_name", type: "char" },{ name: "driver_id", type: "many2one" }, { name: "vehicle_id", type: "many2one" }, { name: "trailer_id", type: "many2one" },{name:"is_active", type:"bool"}, {name:"is_completed", type:"bool"}];
    },
    
}
registry.category("fields").add("trips", tripsField);
