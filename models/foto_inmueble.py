from odoo import fields, models


class FotoInmueble(models.Model):
    """Foto asociadas a un inmueble."""

    _name = "inmo.inmueble.foto"
    _description = "Foto del inmueble"
    _order = "id"

    inmueble_id = fields.Many2one(
        comodel_name="inmo.inmueble",
        string="Inmueble",
        ondelete="cascade",
    )
    descripcion = fields.Char(string="Descripción")
    foto = fields.Image(max_width=1920, max_height=1920, string="Foto")
