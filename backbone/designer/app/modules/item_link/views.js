define([
    "app",

    // Libs
    "backbone",
    "jqueryui"

],

    function (app, Backbone) {

        var Views = {};

        Views.Add = Backbone.Modal.extend({
            initialize:function (options) {

                this.form = new Backbone.Form({

                    data:this.model.toJSON(),

                    //Schema
                    schema:{
                        item:{ type:'Object', title:"Name", subSchema:{
                            layer:{ type:'Hidden'},
                            target:{ type:'Hidden'},
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
                            name:{ type:'Text', validators:['required'] }
                        }},
                        url:{ type:'Text', validators:['required'] }
                    }
                })

                this.options.title = 'Add Content'
                this.options.content = ''

                this.on('ok', this.save, this);
                this.on('cancel', this.cancel, this);
            },

            afterRender:function(el){
                $(el).find('.modal-body p').prepend(this.form.render().el)
                this.open()
            },

            save:function () {
                var self = this;
                this.preventClose();

                if (this.form.validate() == null) {
                    var data = self.form.getValue();

                    this.model.save(data, {
                        success:function () {
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

        return Views;

    });
