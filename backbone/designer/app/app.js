define([
    // Libs
    "jquery",
    "lodash",
    "backbone",
    "bootstrap",
    "fileupload",

    // Plugins
    "plugins/backbone-forms",
    "plugins/backbone.forms-lm.patch",
    "plugins/list",
    "plugins/backbone.forms.file-uploader",
    "plugins/backbone.forms.image-uploader",
    "plugins/backbone.forms.gallery-image-uploader",
    //"plugins/backbone.forms-lm.patch",
    "plugins/backbone.layoutmanager",
    "plugins/backbone-tastypie",
//    "plugins/backbone-relational",
    "plugins/bootstrap",
    "plugins/backbone.bootstrap-modal",
    "plugins/backbone.modal"

],

    function ($, _, Backbone) {
        // Create or attach to the global JavaScript Template cache.
        var JST = window.JST = window.JST || {};

        // Configure LayoutManager
        Backbone.LayoutManager.configure({
            paths:{
                layout:"/static/designer/app/templates/layouts/",
                template:"/static/designer/app/templates/"
            },

            fetch:function (path) {
                path = path + ".html";

                if (!JST[path]) {
                    $.ajax({ url:path, async:false, cache:false }).then(function (contents) {
                        JST[path] = _.template(contents);
                    });
                }

                return JST[path];
            }
        });

        return {
            // Create a custom object with a nested Views object
            module:function (additionalProps) {
                return _.extend({ Views:{} }, additionalProps);
            },

            // Keep active application instances namespaced under an app object.
            app:_.extend({}, Backbone.Events)
        };
    });
