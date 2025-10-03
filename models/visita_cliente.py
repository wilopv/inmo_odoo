from odoo import fields, models


class VisitaInmueble(models.Model):
    """Visitas de clientes a un inmueble usando el calendario estándar."""

    _inherit = "calendar.event"

    inmueble_id = fields.Many2one(
        comodel_name="inmo.inmueble",
        string="Inmueble",
        required=True,
        ondelete="cascade",
    )
    cliente_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
        required=True,
    )
