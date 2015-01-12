define([
    'app',

    // Libs
    'backbone',
    'jqueryui'
],

    function(app, Backbone) {

        var Views = {};

        Views.List = Backbone.View.extend({
            tagName: 'ul',
            className: 'items elements',

            initialize: function() {
                console.log('- initialize: item/views.list');
                var self = this;

                this.collection.on('add', function(model) {
                    this.insertView(new Views.Item({ model:model, collection:self.collection })).render();
                }, this);

                this.collection.on('remove', function(model) {
                    this.getView(function(view) {
                        return view.model === model;
                    }).remove();
                }, this);

                this.collection.on('reset', function(coll, mod) {
                    this.render();
                }, this)
            },

            render: function(manage) {
                console.log('- render: item/views.list');
                var self = this;

                this.collection.each(function(item) {
                    this.insertView(new Views.Item({
                        model:item,
                        collection:self.collection
                    }));
                }, this);

                return manage(this).render();
            }
        });

        Views.Item = Backbone.View.extend({
            template: 'item/item',
            tagName: 'li',
            className: 'element',

            cleanup: function() {
                console.log('cleanup');

                this.model.unbind('destroy');
                this.model.unbind('change');
                this.model.unbind('add');
                this.model.unbind('remove');

                // or -> this.model.off(null, null, this); ? I don't know...
            },

            initialize: function() {
                this.model.on('change', function(mod) {
                    this.render();
                }, this);
            },
            events: {
                'mouseover': 'show_edit_buttons',
                'mouseout': 'hide_edit_buttons',
                'mousedown': 'on_mousedown',
                'click': 'on_click',
                'click a.delete_item_link': 'delete_item_click',
                'click a.center_item_link': 'center_item_click'
            },

            on_click: function(e) {
                e.stopImmediatePropagation();
                e.preventDefault();
                this.collection.selectItem(this.model);
            },

            on_mousedown: function(e) {
                $('.target-item').removeClass('selected');
                $('.target-region').hide();
                $(this.el).find('.target-item').addClass('selected');
                $(this.el).find('.target-region').show();
            }, 

            render: function(manage) {
                console.log('- render: item/views.item');
                var self = this;

                return manage(this).render().then(function() {

                    if (this.model.get('is_active')) {
                        $(this.el).addClass('is_active');
                    }
                    else {
                        $(this.el).removeClass('is_active');
                    }

                    $(this.el).find('.draggable').draggable({
                        //handle: 'a.move_item_link',
                        containment: '.ui-droppable',

                        start: function(event, ui) {
                            self.collection.selectItem(self.model);
                        },

                        stop: function(event, ui) {
                            var coord = $(this).position();
                            var field = $(this).attr('data-position');
                            var field_x = field + '_x';
                            var field_y = field + '_y';
                            var area_width = $('.trackable_image_img').width();
                            var area_height = $('.trackable_image_img').height();

                            var x = self.model.get(field_x);
                            x = coord.left;
                            /*
                            if (x < 0) {
                                x = 0;
                            } else if (x > area_width) {
                                x = area_width - $(this).width();
                            }
                            */

                            var y = self.model.get(field_y);
                            y = coord.top;
                            /*
                            if (y < 0) {
                                y = 0;
                            } else if (y > area_height) {
                                y = area_height - $(this).height();
                            }
                            */

                            var position = {};
                            position[field_x] = x;
                            position[field_x + '_p'] = (100 * (x/area_width)).toFixed(5);
                            position[field_y] = y;
                            position[field_y + '_p'] = (100 * (y/area_height)).toFixed(5);
                            self.model.set(position);
                            self.model.save()
                        }
                    });

                    $(this.el).find('.resizable').resizable({
                            handles: 'all',
                            minHeight:70,
                            minWidth:70,
                            stop: function(e, ui) {
                                var w = ui.size.width;
                                var h = ui.size.height;
                                var x = self.model.get('region_x');
                                var y = self.model.get('region_y');
                                var area_width = $('.trackable_image_img').width();
                                var area_height = $('.trackable_image_img').height();

                                x = ui.position.left;
                                /*
                                if (x < 0) {
                                    w += x;
                                    x = 0;
                                }
                                */

                                y = ui.position.top;
                                /*
                                if (y < 0) {
                                    h += y;
                                    y = 0;
                                }
                                */

                                self.model.set({
                                    'region_width': w,
                                    'region_width_p': (100 * (w/area_width)).toFixed(5),
                                    'region_height': h,
                                    'region_height_p': (100 * (h/area_height)).toFixed(5),
                                    'region_x': x,
                                    'region_x_p': (100 * (x/area_width)).toFixed(5),
                                    'region_y': y,
                                    'region_y_p': (100 * (y/area_height)).toFixed(5)
                                });

                                self.model.save();
                            }
                        });

                    /* Set position */
                    var $item = $(this.el).find('[data-position="position"]');
                    $item.css({'position': 'absolute'});
                    $item.css({'top': self.model.get('position_y') + 'px', 'left': self.model.get('position_x') + 'px'});

                    var $region = $(this.el).find('[data-position="region"]');
                    $region.css({'position': 'absolute'});
                    $region.css({'top': self.model.get('region_y') + 'px', 'left': self.model.get('region_x') + 'px'});

                    var reg_width = Math.max(70, self.model.get('region_width'));
                    var reg_height = Math.max(70, self.model.get('region_height'));

                    $region.css({'width':reg_width + 'px', 'height':reg_height + 'px'});
                    if (this.model.get('is_visible')) {
                        $(this.el).find('.target-item').addClass('selected');
                        $(this.el).show();
                    }
                    else {
                        $(this.el).hide();
                    }
                });
            },

            serialize: function() {
                return this.model.toJSON();
            },

            delete_item_click: function(e) {
                e.stopImmediatePropagation();
                e.preventDefault();

                var result = confirm('Sure?');
                if (result) {
                    this.model.destroy({wait:true});
                }
            },

            center_item_click: function(e) {
                e.stopImmediatePropagation();
                e.preventDefault();

                x = this.model.get('region_x');
                y = this.model.get('region_y');
                x += this.model.get('region_width')/2;
                y += this.model.get('region_height')/2;
                this.model.set({'position_x': x, 'position_y': y});
                this.model.save();
            },

            show_edit_buttons: function(e) {
                $(this.el).find('.menu_item_buttons').show();
            },

            hide_edit_buttons: function(e) {
                $(this.el).find('.menu_item_buttons').hide();
            }
        });


        // Property Form

        Views.PropertyForm = Backbone.View.extend({
            template: 'item/property_form',

            initialize: function() {
                this.form = new Backbone.Form({model:this.model, template: 'form_compact'});

                this.collection.on('change', function(mod, val) {
                    var val = this.form.fields.item.getValue();

                    val['position_x'] = mod.get('position_x');
                    val['position_y'] = mod.get('position_y');
                    val['position_x_p'] = mod.get('position_x_p');
                    val['position_y_p'] = mod.get('position_y_p');

                    val['region_x'] = mod.get('region_x');
                    val['region_y'] = mod.get('region_y');
                    val['region_x_p'] = mod.get('region_x_p');
                    val['region_y_p'] = mod.get('region_y_p');

                    val['region_width'] = mod.get('region_width');
                    val['region_height'] = mod.get('region_height');
                    val['region_width_p'] = mod.get('region_width_p');
                    val['region_height_p'] = mod.get('region_height_p');

                    this.form.fields.item.setValue(val);
                }, this);
            },

            cleanup: function() {
                this.collection.off(null, null, this);
            },

            events: {
                'click .btn-save': 'save',
                'keydown': 'handleEnter'
            },

            handleEnter: function(event) {
                if (event.keyCode == 13) {

                    this.save();
                    event.preventDefault();
                    return false;
                }
            },

            save: function() {
                console.log('saving...');

                var area_width = $('.trackable_image_img').width();
                var area_height = $('.trackable_image_img').height();

                console.log(this.form);
                var src = this.form.fields.item.getValue();
                var dst = this.model.attributes.item;

                /* Check if percent properties changed */
                if (src.position_x_p != dst.position_x_p) {
                    src.position_x = Math.round((src.position_x_p/100) * area_width);
                } else if (src.position_x != dst.position_x) {
                    src.position_x_p = ((src.position_x/area_width) * 100).toFixed(5);
                }

                if (src.position_y_p != dst.position_y_p) {
                    src.position_y = Math.round((src.position_y_p/100) * area_height);
                } else if (src.position_y != dst.position_y) {
                    src.position_y_p = ((src.position_y/area_height) * 100).toFixed(5);
                }

                if (src.region_x_p != dst.region_x_p) {
                    src.region_x = Math.round((src.region_x_p/100) * area_width);
                } else if (src.region_x != dst.region_x) {
                    src.region_x_p = ((src.region_x/area_width) * 100).toFixed(5);
                }


                if (src.region_y_p != dst.region_y_p) {
                    src.region_y = Math.round((src.region_y_p/100) * area_height);
                } else if (src.region_y != dst.region_y) {
                    src.region_y_p = ((src.region_y/area_height) * 100).toFixed(5);
                }

                if (src.region_width_p != dst.region_width_p) {
                    src.region_width = Math.round((src.region_width_p/100) * area_width);
                } else if (src.region_width != dst.region_width) {
                    src.region_width_p = ((src.region_width/area_width) * 100).toFixed(5);
                }

                if (src.region_height_p != dst.region_height_p) {
                    src.region_height = Math.round((src.region_height_p/100) * area_height);
                } else if (src.region_height != dst.region_height) {
                    src.region_height_p = ((src.region_height/area_height) * 100).toFixed(5);
                }

                var metadata = src.metadata;

                /* Update form */
                this.form.fields.item.setValue(src);
                console.log(this.form.fields.item);

                if (this.form.commit() == null) {
                    this.model.attributes.item.metadata = metadata;
                    self = this;
                    this.model.save({},
                        {
                            success: function() {
                                var item = self.collection.get('/api/v1/items/' + self.model.get('item').id + '/');
                                item.fetch()
                                console.log('saved');
                            }
                        });
                }
            },

            render: function(manage) {
                return manage(this).render().then(function() {
                    $(this.el).find('.properties_form').html(this.form.render().el);
                    var $first_el = $('.properties_form .control-group:first-child').attr('id', 'item').addClass('tab-pane fade active in');
                    var $last_el = $('.properties_form .control-group:last-child');
                    var $panel = $last_el.parent();
                    var $content = $first_el.nextUntil($last_el).add($last_el);

                    $panel.append('<div id="content" class="tab-pane fade in"></div>').addClass('tab-content');
                    $panel.append('<div id="metadata" class="tab-pane fade in"></div>').addClass('tab-content');
                    $('fieldset #content').append($content);
                    $first_el.find('.field-metadata').appendTo($('fieldset #metadata'));

                    /* Adjust css */
                    $(this.el).find('p.fileUploader').parent().parent().css('margin-left','0px');
                });
            }
        })

        Views.Property = Backbone.View.extend({
            tagName: 'div',

            getContentModel: function(selected_item) {
                if (!$.isEmptyObject(selected_item)) {
                    var content_type = selected_item.get('content').type;

                    var self = this;

                    require(['modules/item_' + content_type], function(module) {

                        var content_collection = new module.Collection();
                        content_collection.fetch({data: {item:selected_item.get('id')}, success: function() {
                            var content_model = content_collection.at(0);
                            self.trigger('content_loaded', content_model);
                        }});
                    });
                }
            },

            initialize: function() {

                var self = this;

                this.collection.on('item_selected', function(mod) {
                    this.getContentModel(mod);
                }, this)

                this.collection.on('remove_selection', function(mod) {
                    /* Deactive items */
                    $('.target-item').removeClass('selected');
                    $('.target-region').hide();

                    var current_view = this.getView(function(view) {
                        return view.model.get('item').id == mod.get('id');
                    });

                    if (current_view) current_view.remove();
                }, this);

                this.on('content_loaded', function(mod) {
                    this.setView(new Views.PropertyForm({
                        model:mod,
                        collection:this.collection
                    })).render();

                }, this);
            }
        });

        return Views;
    });


