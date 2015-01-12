define([
    // Global application context.
    'app',

    // Third-party libraries.
    'backbone',

    // Views
    'modules/item_coupon/views',
    'modules/item'
],
    function (app, Backbone, Views, Item) {
        var ItemCoupon = app.module();

        ItemCoupon.Model = Backbone.Model.extend({
            defaults:{
                'id':null
            },
            schema:{
                item:{
                    type:'NestedModel',
                    model:Item.Model
                },
                code:{type:'Text',validators:['required']},
                url:{type:'Text',validators:['required']},
                description:{type:'Text'},
                image:{ type:Backbone.Form.ImageField}
            }
        });

        ItemCoupon.Collection = Backbone.Collection.extend({
            model:ItemCoupon.Model,
            url:'/api/v1/coupons/'
        });

        ItemCoupon.Views = Views;

        return ItemCoupon;
    }
);

