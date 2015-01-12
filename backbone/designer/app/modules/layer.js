define([
    // Global application context.
    "app",

    // Third-party libraries.
    "backbone",

    // Views
    "modules/layer/views",
    "modules/item"

],

    function (app, Backbone, Views, Item) {
        var Layer = app.module();

        Layer.Model = Backbone.Model.extend({
            urlRoot:'/api/v1/layers/',
            idAttribute:'id',
//            relations:[
//                {
//                    type:Backbone.HasMany,
//                    key:'items',
//                    relatedModel:Item.Model,
//                    includeInJSON:false,
//                    collectionType:Item.VisibleItemsList
//                }
//            ],

            defaults:{
                "is_active":false,
                "is_visible":true
            },

            setActive:function (val) {
                this.set({"is_active":val});
            },
            setVisible:function (val) {
                this.set({"is_visible":val});
            },

            url:function () {
                return this.id ? '/api/v1/layers/' + this.id + '/' : '/api/v1/layers/';
            },
            toggleVisible:function () {
                this.set({'is_visible':!this.get('is_visible')})
            }
        });

        Layer.List = Backbone.Collection.extend({
            model:Layer.Model,
            url:'/api/v1/layers/',


            getActiveLayer:function () {
                return new Layer.List(this.where({is_active:true})).first()
            },

            setActiveLayer:function (layer_id) {

                this.each(function (layer) {
                    if (layer.get('is_active')) {
                        layer.setActive(false)
                    }

                    if (layer.get('is_visible')) {
                        layer.setVisible(false)
                    }

                });

                this.get(layer_id).setActive(true);
                this.get(layer_id).setVisible(true);

                this.trigger('setActiveLayer');
            },

            checkActiveLayer:function () {
                if ($.isEmptyObject(this.getActiveLayer())) {
                    if (this.first()) {
                        this.setActiveLayer(this.first().get('id'))
                    }
                }
            },

            activateFirstLayer:function () {
                this.setActiveLayer(this.first())
            },

            initialize:function () {
                this.on('reset', function () {
                    this.activateFirstLayer()
                }, this)
            }

        });

        Layer.Views = Views;

        return Layer;
    });
