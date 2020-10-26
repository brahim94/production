from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    production_adjustment = fields.Boolean('Régularisation de production')


class StockPicking(models.Model):
    _inherit = "stock.picking"

    manufacturing_order = fields.Many2one('mrp.production', 'Ordre de Fabrication', check_company=True,
                                          help="Ordre de Fabrication à régulariser")
    production_adjustment = fields.Boolean(related='picking_type_id.production_adjustment', readonly=True)
    Vehicle_registration = fields.Char('Immatriculation véhicule')
    transport_order = fields.Char('Ordre de transport')
    # sales_order_id = fields.Many2one('sale.order', 'Réf Commande')
    client_order = fields.Char(related='sale_id.client_order_ref', store=True, string='ordre de client')
    # brahim = fields.Char('brahim')
    disable_button = fields.Boolean('Active', default=False, copy=False)
    qty_hundred = fields.Float('Quantité hundred', compute="_quantity_all")

    # @api.onchange('sales_order_id')
    # def onchange_client_id(self):
    #     self.client_order = self.sales_order_id.client_order_ref

    def do_print_delivery(self):
        return self.env.ref('tech_production.action_report_delivery_id').report_action(self)

    def do_update(self):
        for rec in self:
            serial_numbers_ids = self.env['pack.serial.number'].search([('stock_picking_id', '=', rec.id)])
            serial_numbers_ids.sudo().unlink()
            for line in rec.move_line_ids_without_package:
                line.serial_number_start = False
                line.serial_number_end = False
            rec.do_affect()

    def do_affect(self):
        for rec in self:
            vals = []
            for line in rec.move_line_ids_without_package:
                if not line.product_id.pack_sequence_id:
                    continue
                weight = line.product_id.weight
                if weight <= 0:
                    raise UserError(
                        "Veuillez rensegnier le poid du produit %s " % line.product_id.name)
                if line.qty_done <= 0:
                    raise UserError(
                        "Veuillez renseigner le champ 'Quantité fait' du produit : %s pour pouvoir affecter les numéros de série " % line.product_id.name)

                line.serial_number_start = line.product_id.pack_sequence_id.next_by_id(sequence_date=line.date)
                vals.append({'name': line.serial_number_start,
                             'product_id': line.product_id.id,
                             'stock_picking_id': rec.id,
                             'res_partner_id': rec.partner_id.id,
                             'delivery_date': rec.scheduled_date,
                             })
                weight = line.product_id.weight
                if weight <= 0:
                    raise UserError(
                        "Veuillez rensegnier le poid du produit %s " % line.product_id.name)
                total_pack = (line.qty_done * 100) / weight
                last = False
                for i in range(int(total_pack - 1)):
                    last = line.product_id.pack_sequence_id.next_by_id(sequence_date=line.date)

                    vals.append({'name': last,
                                 'product_id': line.product_id.id,
                                 'stock_picking_id': rec.id,
                                 'res_partner_id': rec.partner_id.id,
                                 'delivery_date': rec.scheduled_date,
                                 })

                if last:
                    line.serial_number_end = last
                line.picking_id.disable_button = True

            if vals:
                self.env['pack.serial.number'].create(vals)

    
    def _quantity_all(self):
        for order in self:
            for line in order.move_line_ids_without_package:
                line.qty_hundred = (line.qty_done * 100) / line.product_id.weight
                order.update({
                    'qty_hundred': line.qty_hundred,
                    }) 
                    
    # def do_affect(self):
    #     for rec in self:
    #         a = b = p = 0
    #         for line in rec.move_line_ids_without_package:
    #             if line.product_id and line.product_id.pack_sequence_id and line.qty_done > 0:
    #                 a = line.product_id.pack_sequence_id.number_next_actual + line.qty_done
    #                 p = (line.qty_done * 100) / line.product_id.weight
    #                 line.write({'serial_number_start': (str(line.product_id.pack_sequence_id.prefix) + '/' + str(
    #                     line.product_id.pack_sequence_id.suffix) + '/' + str(
    #                     line.product_id.pack_sequence_id.number_next_actual))})
    #                 line.write({'serial_number_end': (str(line.serial_number_start) + str(p - 1))})
    #                 line.product_id.pack_sequence_id.write({'number_next_actual': a + 1})
    #                 line.write({'disable_button': True})
    #                 while b < a + 1:
    #                     self.env['pack.serial.number'].create({
    #                         'name': str(b),
    #                         'product_id': line.product_id.id,
    #                         'stock_picking_id': rec.id,
    #                         'res_partner_id': rec.partner_id.id,
    #                         'delivery_date': rec.scheduled_date,
    #                     })
    #                     b = b + 1
    #             else:
    #                 raise UserError(
    #                     "Veuillez vérifier que le champs 'Quantité fait' a une valeur pour affecter un numéro de série ")
    #
    #     return True

    # package_level = self.env['stock.package_level'].create({
    #             'package_id': package.id,
    #             'picking_id': pick.id,
    #             'location_id': False,
    #             'location_dest_id': move_line_ids.mapped('location_dest_id').id,
    #             'move_line_ids': [(6, 0, move_lines_to_pack.ids)],
    #             'company_id': pick.company_id.id,

    # return self.write({'state': 'draft'})


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

    pack_sequence_id = fields.Many2one('ir.sequence', string='Pack Sequence', domain="[('pack_sequence','=',True)]")


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    serial_number_start = fields.Char(string='Début série ')
    serial_number_end = fields.Char(string='Fin série ')
    qty_hundred_id = fields.Float(related="picking_id.qty_hundred", string='quantity hundred')