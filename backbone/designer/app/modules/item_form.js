define([
    // Global application context.
    'app',

    // Third-party libraries.
    'backbone',

    // Views
    'modules/item_form/views',
    'modules/item'
],
    function (app, Backbone, Views, Item) {
        var ItemForm = app.module();

        ItemForm.Model = Backbone.Model.extend({
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

        ItemForm.Collection = Backbone.Collection.extend({
            model:ItemForm.Model,
            url:'/api/v1/forms/'
        });

        ItemForm.Views = Views;

        return ItemForm;
    }
);

