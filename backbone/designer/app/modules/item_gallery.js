define([
    // Global application context.
    'app',

    // Third-party libraries.
    'backbone',

    // Views
    'modules/item_gallery/views',
    'modules/item'
],
    function (app, Backbone, Views, Item) {
        var ItemGallery = app.module();

        Backbone.Form.editors.List.Modal.ModalAdapter = Backbone.BootstrapModal;

        ItemGallery.ImageModel = Backbone.Model.extend({
            defaults: {
                name:'Unnamed',
                order:0
            },
            schema:{

                name:      {type: 'Text'},
                order:     {type: 'Text'},
                image:     {type:Backbone.Form.FileField, validators:['required']}
            }


        });

        ItemGallery.ImageList = Backbone.Collection.extend({
            model:ItemGallery.ImageModel,
            comparator: function(model) {
                return model.get('order');
            },
            nextOrder: function() {
                if (!this.length) return 0;
                return this.last().get('order') + 1;
            }
        });



        ItemGallery.Model = Backbone.Model.extend({
            defaults:{
                'id':null
            },
            schema:{
                item:{
                    type:'NestedModel',
                    model:Item.Model
                },
                images:      {
                    type: 'List', itemType: 'NestedModel', model: ItemGallery.ImageModel, itemToString: function(i){return i.name}}
            },

            initialize:function () {
                // images
                this.images = new ItemGallery.ImageList();

                if (this.get('id')) {
                    this.images.url = '/api/v1/galleries/' + this.get('id') + '/images/';
                    this.images.fetch()
                }

            }
        });

        ItemGallery.Collection = Backbone.Collection.extend({
            model:ItemGallery.Model,
            url:'/api/v1/galleries/'
        });

        ItemGallery.Views = Views;

        return ItemGallery;
    }
);

