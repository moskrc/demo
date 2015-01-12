define([
    "app",

    // Libs
    "backbone",
    "jqueryui"
],

    function (app, Backbone) {

        var Views = {};

        Views.List = Backbone.View.extend({
            tagName:"ul",
            className:"tools",

            initialize:function () {
                this.collection.on("reset", function () {
                    this.render();
                }, this);
            },
            render:function (manage) {
                console.log('- render: available_content/views.list')
                this.collection.each(function (item) {
                    this.insertView(new Views.Item({
                        model:item
                    }));
                }, this);

                return manage(this).render();
            }
        });


        Views.Item = Backbone.View.extend({
            template:"available_content/item",
            tagName:"li",
            className:"tool",

            events:{
                'mouseover':'hightlight',
                'mouseout':'highlight_reset'
            },

            initialize:function () {
                this.model.on("change", function () {
                    this.render();
                }, this);

                this.model.on("destroy", function () {
                    this.remove();
                }, this);
            },


            render:function (manage) {
                return manage(this).render().then(function () {
                    var $el = $(this.el);
                    $el.attr('rel', this.model.get('name'));
                    $el.attr('title', this.model.get('title'));

                    $el.draggable({
                        zIndex:99999,
                        revert:"invalid",
                        helper:function () {
                            var $helper = $('<div class="target-item"></div>');
                            var $icon = $el.find('div.icon');
                            $icon.clone().appendTo($helper);
                            return $helper;
                        }
                    });
                });
            },

            serialize:function () {
                return this.model.toJSON();
            },

            hightlight:function (e) {
                var $li = $(this.el);
                var $icon = $li.find('div.icon');
                $li.css({
                    'background-image': 'url("/static/images/plugins/icons.png")',
                    'background-position': '-66px 0'
                });
                $icon.addClass('active');
            },

            highlight_reset:function (e) {
                var $li = $(this.el);
                var $icon = $li.find('div.icon');
                $li.css('background-image', 'none');
                $icon.removeClass('active');
            }
        });


        return Views;

    });
