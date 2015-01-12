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

                        is_file:{ type:'Checkbox', editorClass:'video_type', title:'Upload File' },
                        url:{ type:'Text', fieldClass:'video_url', validators:[
                            function checkUrl(value, formValues) {
                                var err = { type:'required', message:'Enter URL Please'};
                                if (formValues.is_file == false && value == '') return err;
                            }
                        ] },
                        video:{ type:Backbone.Form.FileField, fieldClass:'video_file', validators:[
                            function checkFile(value, formValues) {
                                var err = { type:'required', message:'Upload File Please'};
                                if (formValues.is_file && !formValues.video) return err;
                            }
                        ] },
                        is_ar_video: {type: 'Checkbox', title: 'Is AR Video'}

                    }
                })

                this.options.title = 'Add Content'
                this.options.content = ''

                this.on('ok', this.save, this);
                this.on('cancel', this.cancel, this);
            },

            afterRender:function(el){
                $(el).find('.modal-body p').prepend(this.form.render().el)
                var self = this
                this.open()

                $(el).find('.video_type').bind('change',function (e) {
                    if ($(this).is(':checked')) {
                        $(el).find('.video_file').show();
                        $(el).find('.video_url').find('input').val('').end().hide();
                    } else {
                        self.form.fields['video'].setValue('')
                        $(el).find('.video_file').find('.upload_preview').remove().end().hide()
                        $(el).find('.video_url').show();
                    }
                }).change();

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
