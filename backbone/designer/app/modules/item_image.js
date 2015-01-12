define([
    // Global application context.
    'app',

    // Third-party libraries.
    'backbone',

    // Views
    'modules/item_image/views',
    'modules/item'
],
    function (app, Backbone, Views, Item) {
        var ItemImage = app.module();

        ItemImage.Model = Backbone.Model.extend({
            defaults:{
                'id':null,
                'image':''
            },
            schema:{
                item:{
                    type:'NestedModel',
                    model:Item.Model
                },
                image:{
                    type:Backbone.Form.ImageField, validators:['required'],
                    validators:['required']
                }
            }
        });

        ItemImage.Collection = Backbone.Collection.extend({
            model:ItemImage.Model,
            url:'/api/v1/images/'
        });

        ItemImage.Views = Views;

        return ItemImage;
    }
);

