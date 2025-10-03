from odoo import _, api, fields, models


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

    def _build_visita_name(self, cliente, inmueble):
        """Construye el nombre del evento de visita a
        partir del cliente y el inmueble."""

        cliente_name = cliente.display_name if cliente else _("Cliente")
        inmueble_name = inmueble.display_name if inmueble else _("Inmueble")
        return _("Visita de %s a %s") % (cliente_name, inmueble_name)

    def _ensure_visita_fields(self, vals, cliente_id=None, inmueble_id=None):
        """Completa `name` y `categ_ids` para identificar la visita."""
        vals = vals.copy()
        cliente = self.env["res.partner"].browse(cliente_id) if cliente_id else None
        inmueble = (
            self.env["inmo.inmueble"].browse(inmueble_id) if inmueble_id else None
        )

        if cliente and inmueble:
            vals["name"] = self._build_visita_name(cliente, inmueble)

        categ = self.env.ref(
            "inmo_odoo.calendar_event_type_visita", raise_if_not_found=False
        )
        if categ:
            vals["categ_ids"] = [(6, 0, [categ.id])]

        return vals

    @api.model
    def create(self, vals):
        """Antes de crear, ajusta los valores
        para que la visita quede bien identificada."""

        vals = self._ensure_visita_fields(
            vals,
            cliente_id=vals.get("cliente_id"),
            inmueble_id=vals.get("inmueble_id"),
        )
        return super().create(vals)

    def write(self, vals):
        """Si cambian cliente o inmueble, actualiza el título
        y categoría del evento."""

        if {"cliente_id", "inmueble_id"} & vals.keys() and not self.env.context.get(
            "skip_visita_autofill"
        ):
            for record in self:
                updated_vals = record._ensure_visita_fields(
                    vals,
                    cliente_id=vals.get("cliente_id", record.cliente_id.id),
                    inmueble_id=vals.get("inmueble_id", record.inmueble_id.id),
                )
                super(
                    VisitaInmueble, record.with_context(skip_visita_autofill=True)
                ).write(updated_vals)
            return True
        return super().write(vals)
