define([
    'app',

    // Libs
    'backbone',
    'jqueryui'
],
    function (app, Backbone) {
        var Views = {};

        Views.Add = Backbone.Modal.extend({
            initialize:function (options) {
                this.form = new Backbone.Form({
                    data:this.model.toJSON(),

                    schema:{
                        item:{
                            type:'Object',
                            title:'Name',
                            subSchema:{
                                layer:{type:'Hidden'},
                                target:{type:'Hidden'},
                                content_type:{type:'Hidden'},
                                position_x:{type:'Hidden'},
                                position_y:{type:'Hidden'},
                                region_x: {type: 'Hidden'},
                                region_y: {type: 'Hidden'},
                                position_x_p: {type: 'Hidden'},
                                position_y_p: {type: 'Hidden'},
                                region_x_p: {type: 'Hidden'},
                                region_y_p: {type: 'Hidden'},
                                region_width_p: {type: 'Hidden'},
                                region_height_p: {type: 'Hidden'},
                                name:{type:'Text', validators:['required']}
                            }
                        }
                    }
                });

                this.options.title = 'Add Gallery'
                this.options.content = ''

                this.on('ok', this.save, this);
                this.on('cancel', this.cancel, this);

                this.insertView('.modal-body p',new Views.Uploader({collection:this.model.images}))
            },

            afterRender:function(el){
                $(el).find('.modal-body p form').prepend(this.form.render().el)
                this.open()
            },

            save:function () {
                var self = this;

                this.preventClose();

                if (this.form.validate() == null) {
                    var data = self.form.getValue();

                    if (!data.images) {
                        data['images'] = self.model.images.map(function(i){
                            return {
                                'name':i.get('name'),
                                'image':i.get('short_url'),
                                'order':i.get('order')
                            }
                        })
                    }

                    this.model.save(data, {
                        success:function (model, json_data) {
                            self.close();
                            app.router.navigate('/', true);
                        }
                    });
                }
            },

            cancel:function () {
                app.router.navigate('/');
            }
        });

        Views.Edit = Views.Add.extend({});


        Views.Image = Backbone.View.extend({
            tagName:'li',
            className:'span2',
            template:'item_gallery/image',

            events:{
                'click .edit-item':'editItem',
                'click .remove-item':'removeItem',
                'sortable_drop':'sortable_drop'
            },

            initialize:function(){
                this.model.on("change", function () {
                    this.render()
                }, this);
            },

            sortable_drop: function(event, index) {
                this.$el.trigger('update-sort', [this.model, index]);
            },

            editItem:function () {
                var result = prompt('Enter new name', this.model.get('name'));
                if (result) {
                    this.model.set({name:result})
                }
            },
            removeItem:function () {
                var result = confirm('Sure?');
                if (result) {
                    console.log(this.model)
                    this.model.destroy();
                }
            },
            render: function(manage) {
                console.log('item - render')
                return manage(this).render().then(function(el){
                });
            },

            serialize: function(){
                return this.model.toJSON();
            }
        });

        Views.Images = Backbone.View.extend({
            tagName:'ul',
            className:'thumbnails',

            events: {
                'update-sort': 'updateSort'
            },

            initialize:function(){
                this.collection.on("add", function (model) {
                    this.insertView(new Views.Image({ model:model})).render();
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

            render: function(manage) {
                this.collection.each(function (item) {
                    this.insertView(new Views.Image({
                        model:item
                    }));
                }, this);

                return manage(this).render().then(function(el){
                    $(el).sortable({
                        stop: function(event, ui) {
                            ui.item.trigger('sortable_drop', ui.item.index());
                        }
                    });
                });
            },
            updateSort: function(event, dst_model, position) {
//                var before = dst_model.get('order')
//                var after = position
//                this.collection.at(before).set({ order: after })
//                this.collection.at(after).set({ order: before })

                this.collection.remove(dst_model);

                this.collection.each(function (model, index) {
                    var order = index;
                    if (index >= position)
                        order += 1;
                    model.set('order', order);
                    console.log(model.get('order'))
                });

                dst_model.set('order', position);

                this.collection.add(dst_model.toJSON(), {at: position});

                this.render();
            }

        });

        Views.Uploader = Backbone.View.extend({
            template:"item_gallery/uploader",
            className:'form-horizontal',
            tagName:'form',

            initialize: function(){
                this.insertViews({".gallery-images":new Views.Images({collection:this.collection})})
            },

            serialize: function(){
                return {images:this.collection.length > 0}
            },

            render: function(manage) {
                return manage(this).render().then(function(el){

                    var self = this

                    $(el).find("#fileupload").fileupload({
                        maxNumberOfFiles:100,
                        url: '/uploadify/',
                        dataType: 'json',
                        done: function (e, data) {
                            $.each(data.result, function (index, file) {
                                self.collection.add({
                                    delete_url:file.delete_url,
                                    name:file.name,
                                    path:file.path,
                                    short_url:file.short_url,
                                    thumbnail_path:file.thumb_path,
                                    thumbnail_url:file.thumbnail_url,
                                    url:file.url,
                                    order:self.collection.nextOrder()
                                },{at: 0})
                            });
                        },
                        progressall: function (e, data) {
                            $(el).find('.progress div').css('width', parseInt(data.loaded / data.total * 100, 10) + '%');
                        },
                        start: function () {
                            $(el).find('.progress').show().find('div').css('width', '0%');
                        },
                        stop: function () {
                            $(el).find('.progress').hide()
                        }
                    });
                });
            }
        });

        return Views;
    }
);

