define([
    // Global application context.
    "app",

    // Third-party libraries.
    "backbone",

    // Views
    "modules/target/views",
    "modules/layer",
    "modules/item"

],

    function (app, Backbone, Views, Layer, Item) {

        var Target = app.module();

        Target.Model = Backbone.Model.extend({

            initialize:function () {
                this.url = '/api/v1/targets/' + this.attributes.id + '/';

                // layers
                this.layers = new Layer.List();
                this.layers.url = '/api/v1/targets/' + this.attributes.id + '/layers/'

                // items
                this.items = new Item.List()
                this.items.url = '/api/v1/targets/' + this.attributes.id + '/items/'

                var self = this

                this.layers.on("change:is_visible", function (model) {
                    self.items.each(function (item) {
                        if (item.get('layer') == model.get('resource_uri')) {
                            item.set('is_visible', model.get('is_visible'))
                        }
                        else
                        {
                            item.set('is_visible', false)
                        }
                    });
                })

                this.items.on("reset", function (model) {
                    var active_layer = self.layers.getActiveLayer()
                    self.items.each(function (item) {
                        if (item.get('layer') == active_layer.get('resource_uri')) {
                            item.set('is_visible', active_layer.get('is_visible'))
                        }
                        else
                        {
                            item.set('is_visible', false)
                        }
                    });
                })
            },

            parse: function(response) {
                this.layers.reset(response.layers)
                this.items.reset(response.items)
                return response
            }

        });

        Target.List = Backbone.Collection.extend({
            model:Target.Model,
            url:'/api/v1/targets/'
        });

        Target.Views = Views;

        return Target;
    });
