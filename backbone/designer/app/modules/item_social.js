define([
    // Global application context.
    'app',

    // Third-party libraries.
    'backbone',

    // Views
    'modules/item_social/views',
    'modules/item'
],
    function (app, Backbone, Views, Item) {
        var ItemSocial = app.module();

        ItemSocial.Model = Backbone.Model.extend({
            defaults:{
                'id':null
            },
            schema:{
                item:{
                    type:'NestedModel',
                    model:Item.Model
                },
                url:{
                    type:'Text',
                    validators:['required']
                }
            }
        });

        ItemSocial.Collection = Backbone.Collection.extend({
            model:ItemSocial.Model,
            url:'/api/v1/social/'
        });

        ItemSocial.Views = Views;

        return ItemSocial;
    }
);

