/**
 * Bootstrap Modal wrapper for use with Backbone.
 * 
 * Takes care of instantiation, manages multiple modals,
 * adds several options and removes the element from the DOM when closed
 *
 * @author Charles Davison <charlie@powmedia.co.uk>
 *
 * Events:
 * cancel: The user dismissed the modal
 * ok: The user clicked OK
 */

;(function() {

    //DEPENDENCIES
    //Global object (window in the browser)
    var root = this;

// Alias the libraries from the global object
    var Backbone = root.Backbone;
    var _ = root._;
    var $ = root.$;




  var Modal = Backbone.View.extend({
    template:'dialog',
      className:'modal',

    events: {
      'click .close': function(event) {
        event.preventDefault();

        this.trigger('cancel');
        this.close();
      },
      'click .cancel': function(event) {
        event.preventDefault();

        this.trigger('cancel');
        this.close();
      },
      'click .ok': function(event) {
        event.preventDefault();

        this.trigger('ok');
        this.close();
      },
        'keypress input[type=text]': function(event) {
            if ( event.which == 13 ) {
                event.preventDefault();
                event.stopImmediatePropagation();

                this.trigger('ok');
                this.close();
            }

        }

    },

    initialize: function(options) {
      this.options = _.extend({
        title: null,
        okText: 'OK',
        cancelText: 'Cancel',
        allowCancel: true,
        escape: true,
        animate: true
        //template: template
      }, options);
    },

      serialize:function(){
          data = {
              title:this.options.title,
              okText: 'OK',
              cancelText: 'Cancel',
              allowCancel: true,
              escape: true,
              animate: false
          }
          return data;
      },

      render: function(manage) {
      var $el = this.$el, options = this.options

      if (options.animate) $el.addClass('fade');

      return manage(this).render().then(function(e){
          this.isRendered = true;
          this.afterRender(e)
      });
    },

    afterRender:function(el){
    },

    /**
     * Renders and shows the modal
     */
    open: function() {
      if (!this.isRendered) this.render();

      var $el = this.$el;

      //Create it
      $el.modal({
        keyboard: this.options.allowCancel,
        backdrop: this.options.allowCancel ? true : 'static'
      });


      Modal.count++;
      
      return this;
    },

    /**
     * Closes the modal
     */
    close: function() {
      var self = this,
          $el = this.$el;

      //Check if the modal should stay open
      if (this._preventClose) {
        this._preventClose = false;
        return;
      }

      $el.modal('hide');

      $el.one('hidden', _.bind(this.remove, this));

      Modal.count--;
    },

    /**
     * Stop the modal from closing.
     * Can be called from within a 'close' or 'ok' event listener.
     */
    preventClose: function() {
      this._preventClose = true;
    }
  }, {
    //STATICS

    //The number of modals on display
    count: 0
  });


  //EXPORTS
  //CommonJS
//  if (typeof require == 'function' && module && exports) {
//    module.exports = Modal;
//  }

    Backbone.Modal = Modal;

}).call(this);
