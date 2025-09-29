# from odoo import http


# class InmoOdoo(http.Controller):
#     @http.route('/inmo_odoo/inmo_odoo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inmo_odoo/inmo_odoo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('inmo_odoo.listing', {
#             'root': '/inmo_odoo/inmo_odoo',
#             'objects': http.request.env['inmo_odoo.inmo_odoo'].search([]),
#         })

#     @http.route('/inmo_odoo/inmo_odoo/objects/<model("inmo_odoo.inmo_odoo"):obj>',
#                   auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inmo_odoo.object', {
#             'object': obj
#         })
