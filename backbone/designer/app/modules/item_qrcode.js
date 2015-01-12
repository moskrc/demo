define([
    // Global application context.
    'app',

    // Third-party libraries.
    'backbone',

    // Views
    'modules/item_qrcode/views',
    'modules/item'
],
    function (app, Backbone, Views, Item) {
        var ItemQRCode = app.module();

        ItemQRCode.Model = Backbone.Model.extend({
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

        ItemQRCode.Collection = Backbone.Collection.extend({
            model:ItemQRCode.Model,
            url:'/api/v1/qrcodes/'
        });

        ItemQRCode.Views = Views;

        return ItemQRCode;
    }
);

