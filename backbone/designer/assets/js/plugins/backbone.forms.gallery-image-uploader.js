;(function() {

    //DEPENDENCIES
    //Global object (window in the browser)
    var root = this;

// Alias the libraries from the global object
    var Backbone = root.Backbone;
    var _ = root._;
    var $ = root.$;



    // Editor for backbone-forms.js
    
    FileField = Backbone.Form.editors.Base.extend({

        tagName: 'p',

        initialize: function(options) {
            Backbone.Form.editors.Base.prototype.initialize.call(this, options);
            this.file_url = '';
        },

        render: function() {
            this.template = '\n' +
                    '<% if (field.value) { %>' +
                    '<img class="upload_preview" src="<%= field.file_url %>" height="100px"/>\n'+
                    '<br>\n'+
                    '<% } %>\n'+
                    '<span class="btn success fileinput-button" data-loading-text="loading stuff..." >\n'+
                        '<span>Upload File</span>\n'+
                        '<input id="fileupload" type="file" name="files[]">\n'+
                    '</span>\n' +
                    '</br>\n' +
                    '<div style="margin-bottom: 9px; margin-top: 15px;" class="progress progress-info progress-striped"><div style="width: 0%" class="bar"></div></div>';

            if (this.value && this.value.search('/static/uploads/') < 0){
                this.value = '/static/uploads/'+this.value;
            }

            this.setValue(this.value);
            
            var template = _.template(this.template, {'field':this});
            
            $(this.el).addClass('fileUploader');
            
            $(this.el).html(template);

            var view = this;
            
            $(this.el).find('#fileupload').fileupload({
                    maxNumberOfFiles:1,
                    url: '/uploadify/',
                    dataType: 'json',
                    done: function (e, data) {
                        console.log(data.result);

                        $.each(data.result, function (index, file) {
                            console.log(1111);

                            view.file_url = file.url;


                            if ($(view.el).find('.upload_preview').length > 0)
                            {
                                $(view.el).find('.upload_preview').attr('src',file.thumbnail_url);
                            }
                            else
                            {
                                $(view.el).prepend('<img class="upload_preview" src="'+file.thumbnail_url +'" height="100px"/><br/>\n');
                            }
                        });
                    },
                    // Callback for global upload progress events:
                    progressall: function (e, data) {
                        $(view.el).find('.progress div').css(
                            'width',
                            parseInt(data.loaded / data.total * 100, 10) + '%'
                        );
                    },
                    // Callback for uploads start, equivalent to the global ajaxStart event:
                    start: function () {
                        $(view.el).find('.progress').show()
                        $(view.el).find('.progress').find('div').css('width', '0%');
                    },
                    // Callback for uploads stop, equivalent to the global ajaxStop event:
                    stop: function () {
                        $(view.el).find('.progress').hide()
                    }
            });


            return this;
        },

        getValue: function() {
            if (this.file_url)
            {
                return this.file_url.split('/static/uploads/')[1];
            }
        },

        setValue: function(value) {
            this.file_url = this.value;
        }

    });



    Backbone.Form.GalleryImageField = FileField;

}).call(this);