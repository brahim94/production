from odoo import api, fields, models

class tech_production(models.Model):
    _inherit = "stock.picking.type"

    regularization_prd = fields.Boolean('Regularisation Production')
    #order_prod = fields.Many2one('stock.picking.type', 'Order Fabrication', required=True)

class tech_production_picking_type(models.Model):
    _inherit = "stock.picking"

    order_prod = fields.Many2one('stock.picking', 'Order Fabrication', required=True)
    regularization_id = fields.Boolean(related='picking_type_id.regularization_prd', string='Regularisation production')
