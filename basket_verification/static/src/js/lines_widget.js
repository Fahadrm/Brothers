odoo.define('basket_verification.add_basket',function (require){
  'use strict';
  var core = require('web.core');
  var Widget = require('web.Widget');
  var Dialog = require('web.Dialog');
  var QWeb = core.qweb;
  var LinesWidget = require('stock_barcode.LinesWidget');
  // console.log('LinesWidget',LinesWidget);
  LinesWidget.include({

    events:_.extend({}, LinesWidget.prototype.events,{
      'click .add_basket':'_AddBasket',
    }),
    init: function (parent, page, pageIndex, nbPages) {
        this._super.apply(this, arguments);
        console.log('parent.actionParams',parent.actionParams);
        // this.basket_ids = parent.basket_ids;
        this.action_params = parent.actionParams;
      },
    _AddBasket:function(){
      var self = this;
      var barcode = $('.basket_barcode_input').val();
      var rec = this._rpc({
      // return this._rpc({
        model: 'stock.picking',
        method: 'set_basket',
        args: [this.action_params.id,this.action_params.id,barcode,],
        // args: [this.action_params.id,{
        //   'picking_id': this.action_params.id,
        //   'basket':'B2',
        // }],
      });
      rec.then(function(res){
        console.log('rec',res);
      $('.basket_barcode_input').val('');
      var message = res['result'];
      if (res['status'] == true){
        Dialog.alert(self, message);
      }
      else{
        Dialog.alert(self, message);
      }
    });
    },
  });
});
