# from odoo import models, fields, api


# class inmo_odoo(models.Model):
#     _name = 'inmo_odoo.inmo_odoo'
#     _description = 'inmo_odoo.inmo_odoo'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
