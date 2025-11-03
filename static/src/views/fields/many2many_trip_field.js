/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { usePopover } from "@web/core/popover/popover_hook";
import { registry } from "@web/core/registry";
import {
    many2ManyTagsField,
    Many2ManyTagsField,
} from "@web/views/fields/many2many_tags/many2many_tags_field";
import { TagsList } from "@web/core/tags_list/tags_list";
import { AvatarMany2XAutocomplete } from "@web/views/fields/relational_utils";

export class Many2ManyTripField extends Many2ManyTagsField {
    static template = "tms_shipment.Many2ManyTripField";
    static components = {
        Many2XAutocomplete: AvatarMany2XAutocomplete,
        TagsList,
    };
    static props = {
        ...Many2ManyTagsField.props,
        withCommand: { type: Boolean, optional: true },
    };
    getTagProps(record) {
        console.debug("record:",record);
        var driver = record.data.driver_id ? record.data.driver_id[1] : false;
        var vehicle = record.data.vehicle_id ? record.data.vehicle_id[1] : false;
        return {
            ...super.getTagProps(record),
            img: `/web/image/${this.relation}/${record.resId}/avatar_128`,
            driver: driver,
            vehicle: vehicle,
            
        };
    }
}

export const many2ManyTripField = {
    ...many2ManyTagsField,
    component: Many2ManyTripField,
    relatedFields: (fieldInfo) => {
        return [...many2ManyTagsField.relatedFields(fieldInfo), { name: "driver_id", type: "many2one" },{ name: "vehicle_id", type: "many2one" },];
    },
    
    extractProps({ viewType }, dynamicInfo) {
        const props = many2ManyTagsField.extractProps(...arguments);
        props.withCommand = viewType === "form" || viewType === "list";
        props.domain = dynamicInfo.domain;
        return props;
    },
};

registry.category("fields").add("many2many_trip", many2ManyTripField);

export class ListMany2ManyTripField extends Many2ManyTripField {
    itemsVisible = 5;
}

export const listMany2ManyTripField = {
    ...many2ManyTripField,
    component: ListMany2ManyTripField,
};

registry.category("fields").add("list.many2many_trip", listMany2ManyTripField);

export class Many2ManyTripFieldPopover extends Many2ManyTripField {
    static template = "tms_shipment.Many2ManyTripFieldPopover";
    static props = {
        ...Many2ManyTripField.props,
        close: { type: Function },
    };

    setup() {
        super.setup();
        const originalUpdate = this.update;
        this.update = async (recordList) => {
            await originalUpdate(recordList);
            await this._saveUpdate();
        };
    }

    async deleteTag(id) {
        await super.deleteTag(id);
        await this._saveUpdate();
    }

    async _saveUpdate() {
        await this.props.record.save({ reload: false });
        // manual render to dirty record
        this.render();
        // update dropdown
        this.autoCompleteRef.el?.querySelector("input")?.click();
    }

    get tags() {
        return super.tags.reverse();
    }
}

export const many2ManyTripFieldPopover = {
    ...many2ManyTripField,
    component: Many2ManyTripFieldPopover,
};
registry.category("fields").add("many2many_trip_popover", many2ManyTripFieldPopover);

export class KanbanMany2ManyTripFieldTagsList extends TagsList {
    static template = "tms_shipment.KanbanMany2ManyTripFieldTagsList";

    static props = {
        ...TagsList.props,
        popoverProps: { type: Object },
        readonly: { type: Boolean, optional: true },
    };
    setup() {
        super.setup();
        this.popover = usePopover(Many2ManyTripFieldPopover, {
            popoverClass: "o_m2m_trip_field_popover",
            closeOnClickAway: (target) => !target.closest(".modal"),
        });
    }
    get visibleTagsCount() {
        return this.props.itemsVisible;
    }
    openPopover(ev) {
        if (this.props.readonly) {
            return;
        }
        this.popover.open(ev.currentTarget.parentElement, {
            ...this.props.popoverProps,
            readonly: false,
            canCreate: false,
            canCreateEdit: false,
            canQuickCreate: false,
            placeholder: _t("Search users..."),
        });
    }
    get canDisplayQuickAssignAvatar() {
        return !this.props.readonly && !(this.props.tags && this.otherTags.length);
    }
}

export class KanbanMany2ManyTripField extends Many2ManyTripField {
    static template = "tms_shipment.KanbanMany2ManyTripField";
    static components = {
        ...Many2ManyTripField.components,
        TagsList: KanbanMany2ManyTripFieldTagsList,
    };
    static props = {
        ...Many2ManyTripField.props,
        isEditable: { type: Boolean, optional: true },
    };
    itemsVisible = 10;

    get popoverProps() {
        const props = {
            ...this.props,
            readonly: false,
        };
        delete props.isEditable;
        return props;
    }
    get tags() {
        return super.tags.reverse();
    }
}

export const kanbanMany2ManyTripField = {
    ...many2ManyTripField,
    component: KanbanMany2ManyTripField,
    extractProps(fieldInfo, dynamicInfo) {
        const props = many2ManyTripField.extractProps(...arguments);
        props.isEditable = !dynamicInfo.readonly;
        return props;
    },
};

registry.category("fields").add("kanban.many2many_trip", kanbanMany2ManyTripField);
