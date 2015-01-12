define([
    "app",

    // Libs
    "backbone",

    'modules/item',
    "jqueryui"
],

    function (app, Backbone, Item) {

        var Views = {};

        Views.Area = Backbone.View.extend({
            initialize:function () {
                console.log('- initialize: target/views.block');

                this.insertView(new Item.Views.List({
                    collection:this.model.items
                }));

                this.insertView(new Views.Image({
                    model:this.model
                }));

            },
            events:{
                'drop':'handleDrop'
            },

            render:function (manage) {
                return manage(this).render().then(function () {
                    $(this.el).droppable({hoverClass:'ui-state-active', accept:"div.available_items ul li.ui-draggable"});
                });
            },
            handleDrop:function (event, ui) {

                var area_position = $(this.el).position();

                var position_x = Math.max(0, ui.offset.left - area_position.left - 5);
                position_x = Math.round(position_x);
                var position_y = Math.max(0, ui.offset.top - area_position.top - 5);
                position_y = Math.round(position_y);

                var active_layer = this.model.layers.getActiveLayer();

                if (!$.isEmptyObject(active_layer)) {
                    app.router.navigate('/add/' + ui.draggable.attr('rel') + '/' + active_layer.get('id') + '/' + position_x + '/' + position_y + '/', true);
                }
                else {
                    alert('Select active layer first, please');
                }

                return false;
            }
        });

        Views.Image = Backbone.View.extend({
            template:"target/image",
            className:'image',

            initialize:function () {
                console.log('- initialize: target/views.image');
                this.model.on("change", this.render, this);
            },
            events:{
                'click':'removeSelection'
            },

            render:function (manage) {
                console.log('- render: target/views.image');
                return manage(this).render().then(function () {
                });
            },

            removeSelection:function () {
                this.model.items.removeSelection();
            },

            serialize:function () {
                return {'target':this.model.toJSON()}
            }
        });

        Views.Navigator = Backbone.View.extend({
            template:'target/navigator',
            className:'nav',

            initialize:function () {
                console.log('- initialize: target/views.navigator');
                this.model.on('change', this.render, this);
            },

            render:function (manage) {
                console.log('- render: target/views.image');
                return manage(this).render().then(function () {
                });
            },

            serialize:function () {
                return {'target':this.model.toJSON()};
            }
        });

        return Views;
    });

