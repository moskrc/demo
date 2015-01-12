define([
    // Global application context.
    'app',

    // Third-party libraries.
    'backbone',

    // Views
    'modules/item/views'
],

    function(app, Backbone, Views) {
        var Item = app.module();

        Item.Model = Backbone.Model.extend({
            defaults: {
                'id':null,
                'is_selected':false,
                'is_visible':true,
                'region_width':70,
                'region_height':70,
                'auto_start': false
            },
            schema: {
                id: {type: 'Hidden'},

                name: {type: 'Text', validators:['required'], title: 'Name', help: 'Name'},

                region_x: {type: 'Number', title: 'Region X', help: 'Region X'},
                region_x_p: {type: 'Number', title: 'Region X %', help: 'Region X %'},
                region_y: {type: 'Number', title: 'Region Y', help: 'Region Y'},
                region_y_p: {type: 'Number', title: 'Region Y %', help: 'Region Y %'},

                region_width: {type: 'Number', title: 'Region Width', help: 'Region Width'},

                region_width_p: {type: 'Number', title: 'Region Width %', help: 'Region Width %'},
                region_height: {type: 'Number', title: 'Region Height', help: 'Region Height'},
                region_height_p: {type: 'Number', title: 'Region Height %', help: 'Region Height %'},


                position_x: {type: 'Number', title: 'Position X', help: 'Position X'},
                position_x_p: {type: 'Number', title: 'Position X %', help: 'Position X %'},
                position_y: {type: 'Number', title: 'Position Y', help: 'Position Y'},
                position_y_p: {type: 'Number', title: 'Position Y %', help: 'Position Y %'},
                position_z: {type: 'Number', title: 'Position Z', help: 'Position Z'},

                scale_x: {type: 'Number', title: 'Scale X', help: 'Scale X'},
                scale_y: {type: 'Number', title: 'Scale Y', help: 'Scale Y'},
                scale_z: {type: 'Number', title: 'Scale Z', help: 'Scale Z'},
                scale: {type: 'Number', title: 'Scale', help: 'Scale'},

                rotation_x: {type: 'Number', title: 'Rotation X', help: 'Rotation X'},
                rotation_y: {type: 'Number', title: 'Rotation Y', help: 'Rotation Y' },
                rotation_z: {type: 'Number', title: 'Rotation Z', help: 'Rotation Z'},

                auto_start: {type: 'Checkbox', title: 'Auto start', help: 'Auto start'},
                metadata: {type: 'List', itemType: 'Object', subSchema: {
                    key: {type: 'Text'},
                    value: {type: 'Text'}
                }, itemToString: function(data) {
                    return [data.key, data.value].join(': ');
                }},

                layer: {type: 'Hidden'},
                target: {type: 'Hidden'},
                content_type: {type: 'Hidden'}
            },
            save: function(attributes, options) {
                attributes || (attributes = {});

                this.set('region_width', Math.max(this.get('region_width'),70));
                this.set('region_height', Math.max(this.get('region_height'),70));

                Backbone.Model.prototype.save.call(this, attributes, options);
            },
            initialize: function() {

            }

        });

        Item.List = Backbone.Collection.extend({
            model: Item.Model,
            url: '/api/v1/items/',

            initialize: function() {
                this.selected_item = false;

                this.on('remove', function() {
                    this.removeSelection();
                }, this);
            },

            getActiveItem: function() {
                return this.selected_item;
            },

            selectItem: function(item) {
                if (this.selected_item == item) return;

                console.log('select ' + item.get('name'));
                this.selected_item = item;
                this.trigger('item_selected', item);
            },

            removeSelection: function() {
                if (this.selected_item == null) return;
                var was_selected = this.selected_item;

                console.log('remove selection');
                this.selected_item = null;
                this.trigger('remove_selection', was_selected);
            }
        });

        Item.Views = Views;

        return Item;
    });
