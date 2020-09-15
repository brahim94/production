# -*- coding: utf-8 -*-
# from odoo import http


# class TechProduction(http.Controller):
#     @http.route('/tech_production/tech_production/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tech_production/tech_production/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tech_production.listing', {
#             'root': '/tech_production/tech_production',
#             'objects': http.request.env['tech_production.tech_production'].search([]),
#         })

#     @http.route('/tech_production/tech_production/objects/<model("tech_production.tech_production"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tech_production.object', {
#             'object': obj
#         })
