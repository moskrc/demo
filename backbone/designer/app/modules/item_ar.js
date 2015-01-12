define([
    // Global application context.
    'app',

    // Third-party libraries.
    'backbone',

    // Views
    'modules/item_ar/views',
    'modules/item'
],
    function (app, Backbone, Views, Item) {
        var ItemAR = app.module();

        ItemAR.Model = Backbone.Model.extend({
            defaults:{
                'id':null
            },
            schema:{
                item:{
                    type:'NestedModel',
                    model:Item.Model
                },
                model:{ type:Backbone.Form.FileField, validators:['required'], options:{'mini':true} },
                model_ios:{ type:Backbone.Form.FileField, options:{'mini':true}  },
                model_android:{ type:Backbone.Form.FileField, options:{'mini':true}  },
                x_position:{type:'Text'},
                y_position:{type:'Text'},
                z_position:{type:'Text'},
                a_rotation:{type:'Text'},
                b_rotation:{type:'Text'},
                c_rotation:{type:'Text'},
                x_scale:{type:'Text'},
                y_scale:{type:'Text'},
                z_scale:{type:'Text'},
                glyph_enabled:{type:'Checkbox'},

                enable_tracking:{type: 'Checkbox'},
                enable_pan:{type: 'Checkbox'},
                enable_rotate:{type: 'Checkbox'},
                enable_scale:{type: 'Checkbox'},
                drag:{type:'Select',options:[{ val: 'position', label: 'Position' },{ val: 'animate', label: 'Animate' }]},
                pinch:{type:'Select',options:[{ val: 'scale', label: 'Scale' }]},
                twist:{type:'Select',options:[{ val: 'rotate', label: 'Rotate' }]},
                single_tap:{type:'Select',options:[]},
                double_tap:{type:'Select',options:[{ val: 'reset', label: 'Reset' }]},
                swipe_up:{type:'Select',options:[]},
                swipe_down:{type:'Select',options:[]},
                swipe_left:{type:'Select',options:[]},
                swipe_right:{type:'Select',options:[]},
                shake:{type:'Select',options:[{ val: 'reset', label: 'Reset' }]},
                lock_a:{type: 'Checkbox'},
                lock_b:{type: 'Checkbox'},
                lock_c:{type: 'Checkbox'},
                lighting:{type: 'Checkbox', title: 'Default Light'},
                overlay_url:{type:'Text'},
                always_visible:{type:'Checkbox'},
                tracking:{type:'Select',options:[{ val: 'qr', label: 'QR' },{ val: 'glyph', label: 'Glyph' },{val:'frame',label:'Frame'}]},
                zip_archive:{ type:Backbone.Form.FileField, options:{'mini':true}  },
                uses_ar_video: {type: 'Checkbox', title: 'Uses AR Video'}
            }
        });

        ItemAR.Collection = Backbone.Collection.extend({
            model:ItemAR.Model,
            url:'/api/v1/ar/'
        });

        ItemAR.Views = Views;

        return ItemAR;
    }
);

