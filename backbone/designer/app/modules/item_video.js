define([
    // Global application context.
    "app",

    // Third-party libraries.
    "backbone",

    // Views
    "modules/item_video/views",
    "modules/item"
],

    function (app, Backbone, Views, Item) {
        var ItemVideo = app.module();

        ItemVideo.Model = Backbone.Model.extend({
            defaults:{
                "url":'',
                "video":'',
                "id":null
            },
            schema:{
                item:{
                    type:'NestedModel',
                    model:Item.Model
                },
                video:{ type:Backbone.Form.FileField },
                url:{ type:'Text'},
                is_ar_video: {type: 'Checkbox', title: 'Is AR Video'}
            },
            initialize:function () {

            }
        });


        ItemVideo.Collection = Backbone.Collection.extend({
            model:ItemVideo.Model,
            url:'/api/v1/videos/'
        });

        ItemVideo.Views = Views;

        return ItemVideo;
    });
