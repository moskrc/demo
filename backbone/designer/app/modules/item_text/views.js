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
                this.form = new Backbone.Form({model:this.model})

                this.dialog = new Backbone.BootstrapModal({
                    title:'Add Content',
                    content:this.form.render(),
                    animate:false
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


