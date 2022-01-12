odoo.define('mobile_basket_verification.BasketVerification', function (require){
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');
var AbstractAction = require('web.AbstractAction');
var Dialog = require('web.Dialog');

var Qweb = core.qweb;
var _t = core._t;

var BasketWidget = AbstractAction.extend({
  contentTemplate:'BasketVerificationComponent',
  events:{
    // 'change .basket_barcode_input':'_onClickBasketInputChange',
    'input .basket_barcode_input':'_onClickBasketInputChange',
    'click .basket_verify':'_onClickBasketVerify',
  },
  init: function(parent,action){
    this._super.apply(this, arguments);
    this.basketVerificationId = action.context.active_id;

  },
  _onClickBasketInputChange: function(){
    var self = this;
    var barcode = $('.basket_barcode_input').val();
    console.log('barcode',barcode);
    if (barcode !=''){

      return this._rpc({
        model: 'mobile.basket.verification',
        method: 'get_picking_details',
        args: [this.basketVerificationId,barcode],
      }).then(function(res){
        console.log('res111',res);
        console.log('res',res['picking_id']);
        self.picking_id = res['picking_id']
        console.log('self.picking_id',self.picking_id);
        if (res['picking_id'] != false){

          self.picking = res['picking_id']
          self.customer = res['partner_id']
          self.line = res['line_ids']
          var $body = self.$el.find('.o_barcode_lines');
          console.log('isnide if');
          if (res['status'] == true){
            var $lines = $(Qweb.render('basketVerificationLines', {
              picking:res['picking_id'],
              customer:res['partner_id'],
              lines:res['line_ids']
            }));
            $body.prepend($lines);
          }
          var message = res['result'];
          if (res['status'] == false){
            Dialog.alert(self, message);
          }
        }else{
          self.$el.find('.o_barcode_lines').html('');
        }
      });
    }else{
      self.$el.find('.o_barcode_lines').html('');
      
    }
  },
  _onClickBasketVerify: function(){
    var self = this;
    var barcode = $('.basket_barcode_input').val();
    var rec = this._rpc({
      model: 'mobile.basket.verification',
      method: 'basket_verify',
      args: [this.basketVerificationId,barcode],
    });
    rec.then(function(result){
      $('.basket_barcode_input').val('');
      var message = result['result'];
      var status = result['status'];
      Dialog.alert(self,message);
      self.$el.find('.o_barcode_lines').html('');

    });
  },
  start: function() {
    this.$('.o_content').addClass('o_barcode_client_action'); // reuse stylings
      this._super.apply(this, arguments);
    },
});
core.action_registry.add('basket_verification_client_action',BasketWidget);
return BasketWidget;

});
