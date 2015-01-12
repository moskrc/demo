define([
    // Global application context.
    "app",

    // Third-party libraries.
    "backbone",

    // Views
    "modules/item_link/views",
    "modules/item"
],

    function (app, Backbone, Views, Item) {
        var ItemLink = app.module();

        ItemLink.Model = Backbone.Model.extend({
            defaults:{
                "url":'',
                "id":null
            },
            schema:{
                item:{
                    type:'NestedModel',
                    model:Item.Model
                },
                url:{ type:'Text', validators:['required'] }

            }
        });


        ItemLink.Collection = Backbone.Collection.extend({
            model:ItemLink.Model,
            url:'/api/v1/links/'
        });

        ItemLink.Views = Views;

        return ItemLink;
    });
//event:{ type:'Select', validators:['required'], options: [{ val: 'event1', label: 'Event1' },{ val: 'event2', label: 'Event2' }]}