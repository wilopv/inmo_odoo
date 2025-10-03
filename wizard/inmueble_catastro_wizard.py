from __future__ import annotations

from odoo import fields, models
from odoo.exceptions import UserError

from ..models import catastro_service


class InmuebleCatastroWizard(models.TransientModel):
    """Asistente para completar datos de un inmueble usando Catastro."""

    _name = "inmo.inmueble.catastro.wizard"
    _description = "Asistente Catastro para inmuebles"

    inmueble_id = fields.Many2one(
        comodel_name="inmo.inmueble",
        string="Inmueble",
        required=True,
    )
    referencia_catastral = fields.Char(string="Referencia catastral", required=True)

    def action_confirm(self):
        """Consulta Catastro y actualiza los campos del inmueble asociado."""
        self.ensure_one()

        referencia = (self.referencia_catastral or "").strip()
        if not referencia:
            raise UserError("Debe indicar una referencia catastral.")

        datos = catastro_service.consulta_por_referencia(referencia)
        valores = catastro_service.mapear_campos_inmueble(self.env, datos)
        if valores:
            self.inmueble_id.write(valores)

        return {"type": "ir.actions.act_window_close"}
