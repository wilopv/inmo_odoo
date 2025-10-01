from odoo import fields, models


class Inmueble(models.Model):
    """Registro de inmuebles para la inmobiliaria.

    Guarda la información identificativa (nombre comercial, referencia catastral),
    el estado comercial, el tipo de inmueble y los datos básicos de localización
    y características (dirección, municipio/provincia, superficie, habitaciones y baños)
    """

    _name = "inmo.inmueble"
    _description = "Inmueble"

    nombre = fields.Char(string="Nombre comercial", required=True)
    referencia_catastral = fields.Char(string="Referencia catastral", required=False)
    estado = fields.Selection(
        selection=[
            ("disponible", "Disponible"),
            ("reservado", "Reservado"),
            ("vendido", "Vendido"),
            ("alquilado", "Alquilado"),
        ],
        string="Estado",
        default="disponible",
        required=True,
    )
    tipo_inmueble = fields.Selection(
        selection=[
            ("piso", "Piso"),
            ("casa", "Casa"),
            ("local", "Local"),
            ("terreno", "Terreno"),
        ],
        string="Tipo de inmueble",
        required=True,
    )
    calle = fields.Char(string="Calle")
    calle2 = fields.Char(string="Complemento dirección")
    codigo_postal = fields.Char(string="Código postal")
    ciudad = fields.Char(string="Ciudad")
    provincia = fields.Many2one(
        comodel_name="res.country.state",
        string="Provincia",
        help="Provincia o estado donde se ubica el inmueble.",
    )
    id_pais = fields.Many2one(
        comodel_name="res.country",
        string="País",
        help="País donde se ubica el inmueble.",
    )
    superficie_construida = fields.Float(string="Superficie construida (m2)")
    habitaciones = fields.Integer(string="Habitaciones")
    banos = fields.Integer(string="Baños")
