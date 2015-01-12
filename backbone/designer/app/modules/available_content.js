define([
    // Global application context.
    "app",

    // Third-party libraries.
    "backbone",

    // Views
    "modules/available_content/views"

],

    function (app, Backbone, Views) {
        var Available_content = app.module();

        Available_content.Model = Backbone.Model.extend({
            initialize:function (models) {
                this.url = '/api/v1/plugins/';
            }
        });

        Available_content.List = Backbone.Collection.extend({
            model:Available_content.Model,

            initialize:function () {
                this.url = '/api/v1/plugins/'
            },

            findByName:function (name) {
                return _(this.filter(function (data) {
                    return data.get("name") == name;
                }));
            }
        });


        Available_content.Views = Views;

        return Available_content;
    });
