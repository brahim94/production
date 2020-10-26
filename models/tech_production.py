from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

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
    #brahim = fields.Char('brahim')
    disable_button_id = fields.Boolean(related='move_line_ids_without_package.disable_button', string='Actif')
    qty_hundred = fields.Float('Quantité hundred', compute="_quantity_all")
    total_qty_done = fields.Float('Total',compute="_total_all" )
    # @api.onchange('sales_order_id')
    # def onchange_client_id(self):
    #     self.client_order = self.sales_order_id.client_order_ref

    def do_print_delivery(self):
        return self.env.ref('tech_production.action_report_delivery_id').report_action(self)
    
    def do_affect(self):
        for rec in self:
            a = b = p = 0 
            for line in rec.move_line_ids_without_package:
                if line.product_id and line.product_id.pack_sequence_id and line.qty_done > 0:
                    a = line.product_id.pack_sequence_id.number_next_actual + line.qty_done
                    p = (line.qty_done * 100) / line.product_id.weight
                    line.write({'serial_number_start': (str(line.product_id.pack_sequence_id.prefix)+ '/'+str(line.product_id.pack_sequence_id.suffix)+ '/' +str(line.product_id.pack_sequence_id.number_next_actual))})
                    line.write({'serial_number_end': (str(line.serial_number_start)+str(p-1))})
                    line.product_id.pack_sequence_id.write({'number_next_actual': a+1})
                    line.write({'disable_button': True})
                    while b < a+1 :
                        self.env['pack.serial.number'].create({
                        'name': str(b),
                        'product_id': line.product_id.id,
                        'stock_picking_id': rec.id,
                        'res_partner_id': rec.partner_id.id,
                        'delivery_date': rec.scheduled_date,
                        })
                        b = b+1
                else:
                    raise UserError("Veuillez vérifier que le champs 'Quantité fait' a une valeur pour affecter un numéro de série ")

        return True

    #@api.depends('state', 'move_lines.is_quantity_done_editable', 'is_locked')
    
    #    if  self.state == 'assigne' and self.move_lines.is_quantity_done_editable == self.is_locked == False:
    def _quantity_all(self):
        for order in self:
            qty_h = 0.0
            for line in order.move_line_ids_without_package:
                qty_h = (line.qty_done * 100) / line.product_id.weight
            order.update({
                        'qty_hundred': qty_h,
                        })
                    #line.qty_hundred_id = (line.qty_done * 100) / line.product_id.weight
                # else :
                #     qty_h = (line.qty_done * 100) / (line.product_id.weight +1)
                     

    
    def _total_all(self):
        for order in self:
            total_all = 0.0
            for line in order.move_line_ids_without_package:
                total_all += line.qty_done
            order.update({
                'total_qty_done': total_all,
                })

        # package_level = self.env['stock.package_level'].create({
        #             'package_id': package.id,
        #             'picking_id': pick.id,
        #             'location_id': False,
        #             'location_dest_id': move_line_ids.mapped('location_dest_id').id,
        #             'move_line_ids': [(6, 0, move_lines_to_pack.ids)],
        #             'company_id': pick.company_id.id,
        
        
        #return self.write({'state': 'draft'})
  
class SequencePack(models.Model):
    _inherit = "ir.sequence"

    pack_sequence = fields.Boolean(string='Pack Sequence', default=False)

class PackSerialNumber(models.Model):
    _name = "pack.serial.number"

    name = fields.Char(string='Nom')
    product_id = fields.Many2one('product.product', string='Article')
    stock_picking_id = fields.Many2one('stock.picking', string='Nº Bon de livraison')
    res_partner_id = fields.Many2one('res.partner', string='Client')
    delivery_date = fields.Date(string='Date de livraison')

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'le champs _pack sequence name_ doit être unique.')
    ]

class ProductSequencePack(models.Model):
    _inherit = "product.template"

    pack_sequence_id = fields.Many2one('ir.sequence', string='Pack Sequence', domain = "[('pack_sequence','=',True)]")

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    serial_number_start = fields.Char(string='Début de numéro de série ')
    serial_number_end = fields.Char(string='Fin numéro de série ')
    disable_button = fields.Boolean('Active')
    qty_hundred_id = fields.Float(related='picking_id.qty_hundred', string='quantity hundred')
    total_qty_done_id = fields.Float(related='picking_id.total_qty_done', string='Total')
    

    

