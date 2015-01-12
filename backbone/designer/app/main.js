require.config({
    paths: {
        // JavaScript folders
        plugins: "../assets/js/plugins",

        // TODO: Can't add to uglified file :(
        backbone: "../assets/js/libs/backbone",
        bootstrap: "../assets/js/libs/bootstrap",

    },

    shim: {
        backbone:{
            deps:["lodash", "jquery"],
            exports: "Backbone"
        },

        bootstrap:{
            deps:["backbone"]
        },

        jqueryui: {
            deps: ["jquery"]
        },

        fileupload:{
            deps:["jquery.ui.widget"]
        },

        jqueryform: {
            deps: ['jquery']
        },

        // Add the Backbone LocalStorage plugin in
        "plugins/backbone-localstorage":{
            deps:["backbone"]
        },
        "plugins/backbone.layoutmanager":{
            deps:["backbone"]
        },
//        "plugins/backbone-relational":{
//            deps:["backbone"]
//        },
        "plugins/backbone-tastypie":{
            deps:["backbone"]
        },
        "plugins/backbone-forms":{
            deps:["backbone"]
        },
        "plugins/backbone.forms-lm.patch":{
            deps:["plugins/backbone-forms"]
        },

        "plugins/backbone.bootstrap-modal":{
            deps:["bootstrap", "backbone"]
        },
        "plugins/backbone.modal":{
            deps:["bootstrap", "backbone"]
        },
        "plugins/bootstrap":{
            deps:["plugins/backbone-forms"]
        },
        "plugins/list":{
            deps:["plugins/backbone-forms"]
        },
        "plugins/backbone.forms.file-uploader":{
            deps:["plugins/backbone-forms"]
        },
        "plugins/backbone.forms.image-uploader":{
            deps:["plugins/backbone-forms"]
        },
        "plugins/backbone.forms.gallery-image-uploader":{
            deps:["plugins/backbone-forms"]
        }


//        "plugins/backbone.forms-lm.patch":{
//            deps:["plugins/backbone-forms"]
//        }

    }
});

require([
    "app",

    // Libs
    "jquery",
    "backbone",

    // Modules
    "modules/available_content",
    "modules/target",
    "modules/layer",
    "modules/item",

    'jqueryform'

],
    function (app, $, Backbone, Available_content, Target, Layer, Item) {
        $('[data-toggle="dropdown"]').dropdown();  // I don't know why!

        // Params from django app
        app.project_id = parseInt(window.location.pathname.match(new RegExp('designer/(\\d+)/'))[1]);
        app.target_id = parseInt(window.location.pathname.match(new RegExp('target/(\\d+)/'))[1]);

        var Router = Backbone.Router.extend({
            routes:{
                "": "index",
                "add/:content_type/:layer_id/:position_x/:position_y/": "add"
            },

            index:function () {
                // Create item list
                var available_content_list = new Available_content.List();

                // Create target (by URL)
                var target = new Target.Model({id:app.target_id});

                // Create a new layout.
                var main = new Backbone.LayoutManager({
                    template: "main",

                    views:{
                        ".available_items":new Available_content.Views.List({
                            collection:available_content_list
                        }),
                        ".target":new Target.Views.Area({
                            model:target
                        }),
                        ".layers":new Layer.Views.Block({
                            collection:target.layers
                         }),
                        ".properties":new Item.Views.Property({
                            collection:target.items
                        }),
                        ".navigator":new Target.Views.Navigator({
                            model:target
                        })
                    }
                });

                window.main = main;
                $('#main').html(main.$el)
                main.render();

                target.fetch();
                available_content_list.fetch();

                target.layers.on('change',function(model){
                    var active_layer = model.collection.getActiveLayer();
                    console.log(active_layer)

                    if (active_layer) {

                        if (active_layer.get('name') == 'Unnamed' || active_layer.get('name') == 'Main')
                            available_content_list.url = '/api/v1/plugins/';
                        else
                            available_content_list.url = '/api/v1/plugins/search/?q='+active_layer.get('name');
                        available_content_list.fetch();
                    }
                });
            },
            add:function (content_type, layer_id, pos_x, pos_y) {

                var add = new Backbone.LayoutManager({
                    template: "add_item"
                });

                var available_content_list = new Available_content.List();

                available_content_list.on('reset', function () {
                    require(['modules/item_' + content_type.toLowerCase()], function (module) {
                        var area_width = $('.trackable_image_img').width();
                        var area_height = $('.trackable_image_img').height();
                        var pos_x_p = (100 * (pos_x/area_width));
                        var pos_y_p = (100 * (pos_y/area_height));
                        var reg_w_p = (100 * (70/area_width));
                        var reg_h_p = (100 * (70/area_height));

                        var plugin = available_content_list.findByName(content_type).first();
                        var content_model = new module.Model({item:{layer:'/api/v1/layers/' + layer_id + '/', target:'/api/v1/targets/' + app.target_id + '/', content_type:plugin.id, name:'Unnamed', position_x: pos_x, position_y: pos_y, region_x: pos_x, region_y: pos_y, position_x_p: pos_x_p, position_y_p: pos_y_p, region_x_p: pos_x_p, region_y_p: pos_y_p, region_width_p: reg_w_p, region_height_p: reg_h_p}})
                        content_model.collection = new module.Collection();
                        add.insertView('.row', new module.Views.Add({model:content_model}))
                        //new module.Views.Add({model:content_model}).render();
                        add.render()
                    });

                });

                available_content_list.fetch();
            }

        });

        $(function () {
            app.router = new Router();
            Backbone.history.start({ pushState:true, root: "/designer/" + app.project_id + "/target/" + app.target_id + "/"});

        });

        var originalMethod = Backbone.sync;

        Backbone.sync = function(method, model, options) {
            options.timeout = 10000;
            console.log(options)
            var request = originalMethod.call(Backbone, method, model, options);

            request.fail(function(jqXHR, textStatus) {
                if (!jqXHR.responseText) {
                    alert(jqXHR.status+" "+jqXHR.statusText);
                }
                else {
                    alert(jqXHR.responseText);
                }
            });
            return request;
        };



        // All navigation that is relative should be passed through the navigate
        // method, to be processed by the router.  If the link has a data-bypass
        // attribute, bypass the delegation completely.
//        $(document).on("click", "a:not([data-bypass])", function (evt) {
//            // Get the anchor href and protcol
//            var href = $(this).attr("href");
//            var protocol = this.protocol + "//";
//
//            // Ensure the protocol is not part of URL, meaning its relative.
//            if (href && href.slice(0, protocol.length) !== protocol &&
//                href.indexOf("javascript:") !== 0) {
//                // Stop the default event to ensure the link will not cause a page
//                // refresh.
//                evt.preventDefault();
//
//                // `Backbone.history.navigate` is sufficient for all Routers and will
//                // trigger the correct events.  The Router's internal `navigate` method
//                // calls this anyways.
//                Backbone.history.navigate(href, true);
//            }
//        });


        Backbone.Form.setTemplates({
            nestedField: '\
              <div class="field-{{key}}">\
                <div class="field-label">{{title}}</div>\
                <div title="{{title}}" class="field-value">{{editor}}</div>\
              </div>\
            '
        });

    });
