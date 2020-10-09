from odoo import models, fields, api

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    production_adjustment = fields.Boolean('Régularisation de production')

class StockPicking(models.Model):
    _inherit = "stock.picking"

    manufacturing_order = fields.Many2one('mrp.production', 'Ordre de Fabrication', check_company=True, help="Ordre de Fabrication à régulariser")
    production_adjustment = fields.Boolean(related='picking_type_id.production_adjustment', readonly=True)
    Vehicle_registration = fields.Char('Immatriculation véhicule')
    transport_order = fields.Char('Ordre de transport')
    #sales_order_id = fields.Many2one('sale.order', 'Réf Commande')
    client_order = fields.Char(related='sale_id.client_order_ref', store=True, string='ordre de client')

    # @api.onchange('sales_order_id')
    # def onchange_client_id(self):
    #     self.client_order = self.sales_order_id.client_order_ref

    def do_print_delivery(self):
        return self.env.ref('tech_production.action_report_delivery').report_action(self)
  

