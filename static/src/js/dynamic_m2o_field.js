/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";
import { onWillStart, onWillUpdateProps, useState } from "@odoo/owl";

export class DynamicM2OField extends Many2OneField {
    static props = {
        ...Many2OneField.props,
        field_to_show: { type: String, optional: true },
    };
    setup() {
        super.setup();
        
        // Estado local para almacenar el valor extra recuperado por RPC
        this.state = useState({ extraValue: null });

        onWillStart(async () => {
            //console.debug("start",this.props);
            await this.loadExtraValue();
        });

        onWillUpdateProps(async (nextProps) => {
            // Si el ID del Many2one cambia, recargamos el valor
            const oldId = this.getResId(this.props);
            const newId = this.getResId(nextProps);
            if (oldId !== newId) {
                //console.debug("update",nextProps);
                await this.loadExtraValue(nextProps);
            }
        });
    }

    getResId(props) {
        const val = props.record.data[props.name];
        if (Array.isArray(val)) return val[0]; // Es tupla [id, name]
        return val ? val.resId : false; // Es objeto Record
    }

    async loadExtraValue(props = this.props) {
        //console.debug("extra:",props);
        const resId = this.getResId(props);
        const fieldToShow = props.field_to_show;
        
        if (resId && fieldToShow && fieldToShow !== "display_name") {
            try {
                const result = await this.props.record.model.orm.read(
                    this.relation, 
                    [resId], 
                    [fieldToShow]
                );
                if (result && result.length > 0) {
                    this.state.extraValue = result[0][fieldToShow];
                }
            } catch (e) {
                this.state.extraValue = null;
            }
        } else {
            this.state.extraValue = null;
        }
    }

    get displayName() {
        // Si logramos cargar el valor extra por RPC, lo mostramos
        if (this.props.readonly && this.state.extraValue !== null && this.state.extraValue !== false) {
            return String(this.state.extraValue);
        }
        // Fallback al comportamiento original (display_name de la tupla o Record)
        return super.displayName;
    }
}

registry.category("fields").add("dynamic_m2o_field", {
    ...many2OneField,
    component: DynamicM2OField,
    supportedOptions: [
        ...(many2OneField.supportedOptions || []),
        { name: "field_to_show", type: "string" },
    ],
    extractProps: (fieldInfo, dynamicInfo) => {
        const props = many2OneField.extractProps(fieldInfo, dynamicInfo);
        props.field_to_show = fieldInfo.options?.field_to_show || "display_name";
        //console.debug("extract:",props);
        return props;
    },
});
