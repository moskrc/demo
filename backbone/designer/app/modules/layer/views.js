define([
    "app",

    // Libs
    "backbone"
],

    function (app, Backbone) {

        var Views = {};

        Views.Block = Backbone.View.extend({
            tagName:"div",
            className:"layers_block",
            template:"layer/block",

            render:function (manage) {
                console.log('- render: layer/views.block')

                this.insertView(new Views.List({
                    append:function (root, child) {
                        $(root).append(child);
                    },
                    collection:this.collection
                })
                );

                this.insertView(new Views.Controls({
                    append:function (root, child) {
                        $(root).append(child);
                    },
                    collection:this.collection
                })
                );

                return manage(this).render();
            }
        });

        Views.Controls = Backbone.View.extend({
            template:"layer/controls",

            initialize:function () {
                this.collection.on("change", function (coll) {
                    this.render();
                }, this);
            },

            render:function (manage) {
                console.log('- render: layer/views.controls')
                return manage(this).render();
            },

            events:{
                'click button.add_layer':'addLayer',
                'click button.edit_layer':'editLayer',
                'click button.del_layer':'delLayer'
            },

            serialize:function () {
                return {'is_layer_selected':!$.isEmptyObject(this.collection.getActiveLayer())}
            },

            addLayer:function () {
                result = prompt('Layer Name');
                if (result) {
                    this.collection.create({'name':result, 'target':'/api/v1/targets/' + app.target_id + '/'});
                }
            },

            editLayer:function () {

                var obj = this.collection.find(function (layer) {
                    return layer.get("is_active");
                });

                if (!$.isEmptyObject(obj)) {
                    result = prompt('Enter new name', obj.get('name'));
                    if (result) {
                        obj.save({'name':result})
                    }
                }
            },
            delLayer:function () {

                var obj = this.collection.find(function (layer) {
                    return layer.get("is_active");
                });

                if (!$.isEmptyObject(obj)) {
                    result = confirm('Sure?');
                    if (result) {
                        obj.destroy();
                    }
                }

            }


        });


        Views.List = Backbone.View.extend({
            tagName:"select",
            className:"layers",

            initialize:function () {
                this.collection.on("add", function (model) {
                    this.insertView(new Views.Item({ model:model })).render();
                }, this);

                this.collection.on("remove", function (model) {
                    this.getView(function (view) {
                        return view.model === model;
                    }).remove();
                }, this);

                this.collection.on("reset", function (mod, coll) {
                    this.render();
                }, this);
            },
            render:function (manage) {
                console.log('- render: layer/views.list')
                this.collection.each(function (item) {
                    this.insertView(new Views.Item({
                        model:item
                    }));
                }, this);

                return manage(this).render();
            },

            events:{
                'change':'selectionChanged'
            },


            selectionChanged: function (e, a, b) {
                var value = $(e.currentTarget).val();
                console.log("SELECTED", value);

                this.collection.setActiveLayer(value);

//                this.citiesView.collection.url = "countries/" + countryId + "/cities";
//                this.citiesView.collection.fetch();

            }
        });


        Views.Item = Backbone.View.extend({
            tagName:"option",


            initialize:function () {
                this.model.on("change", function () {
                    this.render();
                }, this);

                this.model.on("destroy", function () {
                    this.remove();
                }, this);
            },

            serialize:function () {
                return this.model.toJSON();
            },

            render:function (manage) {
                return manage(this).render().then(function () {
                    var $el = $(this.el);
                    $el.attr('value', this.model.get('id')).html(this.model.get('name'));
                });
            }
        });

        return Views;

    });
