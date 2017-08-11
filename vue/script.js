'use strict';

$(document).ready(function () {
    Vue.config.debug = true;

    new Vue({
        el: '#app',
        data: {
            total_images: 0,
            current_pos: 0,
            current_item: null,
            items: [],

            is_last_item: function () {
                return this.current_pos == this.items.length - 1
            },

            is_first_item: function () {
                return this.current_pos == 0
            }
        },

        methods: {
            'get_current_item': function () {
                return this.items[this.current_pos];
            },
            'like': function (val) {
                this.get_current_item().like = val;

                        if (!val) {
                            val = 'dislike'
                        }
                      this.$http.post('/fav/like/', {action: val, id: this.get_current_item().id}, {emulateJSON: true}).then(function(response) {}, function(response) {});
            },
            'navigate': function (direction) {
                if (direction == 'prev') {
                    this.current_pos -= 1;
                } else {
                    this.current_pos += 1;
                }

                this.current_pos = Math.max(this.current_pos, 0)

                if (this.current_pos > this.items.length - 1) {
                    console.log('done');
                    this.current_pos = this.items.length - 1
                } else {
                    this.updateImage();
                }

            },
            'updateImage': function () {
                this.current_item = this.items[this.current_pos]
            }

        },
        ready: function () {
            this.$http.get('/fav/images/').then(function (response) {
                this.$set('items', response.data.data);
                this.$set('total_images', response.data.data.length)
                this.updateImage();
            }, function (response) {
                alert('error')
            });
        },
    });


    $('#app').focus();
});