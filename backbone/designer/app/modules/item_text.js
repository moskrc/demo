define([
    // Global application context.
    "app",

    // Third-party libraries.
    "backbone",
    // Views
    "modules/item_text/views",
    "modules/item"

],

// NOT USED

    function (app, Backbone, Views, Item) {
        var ItemText = app.module();

        ItemText.Model = Backbone.Model.extend({

            schema:{
                item:{
                    type:'NestedModel',
                    model:Item.Model
                },
                text:{ type:'TextArea', validators:['required'] }
            }//,
//        relations:[
//            {
//                type:Backbone.HasOne,
//                key:'item',
//                relatedModel:Item.Model,
//                includeInJSON:true
//            }
//        ]


        });


        ItemText.Collection = Backbone.Collection.extend({
            model:ItemText.Model,
            url:'/api/v1/texts/'
        });

        ItemText.Views = Views;

        return ItemText;
    });
