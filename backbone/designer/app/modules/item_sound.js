define([
    // Global application context.
    "app",

    // Third-party libraries.
    "backbone",

    // Views
    "modules/item_sound/views",
    "modules/item"
],

    function (app, Backbone, Views, Item) {
        var ItemSound = app.module();

        ItemSound.Model = Backbone.Model.extend({
            defaults:{
                "event":'',
                "sound":'',
                "id":null
            },
            schema:{
                item:{
                    type:'NestedModel',
                    model:Item.Model
                },
                sound:{ type:'Text', validators:['required'] },
                event:{ type:'Select', validators:['required'], options:[
                    { val:'event1', label:'Event1' },
                    { val:'event2', label:'Event2' }
                ]}

            }
        });


        ItemSound.Collection = Backbone.Collection.extend({
            model:ItemSound.Model,
            url:'/api/v1/sounds/'
        });

        ItemSound.Views = Views;

        return ItemSound;
    });
