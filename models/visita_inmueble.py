from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class VisitaInmueble(models.Model):
    """Visitas de clientes a un inmueble usando el calendario estándar."""

    _inherit = "calendar.event"

    inmueble_id = fields.Many2one(
        comodel_name="inmo.inmueble",
        string="Inmueble",
        ondelete="cascade",
    )
    cliente_id = fields.Many2one(
        comodel_name="res.partner",
        string="Cliente",
    )

    def _build_visita_name(self, cliente, inmueble):
        """Construye el nombre del evento de
        visita a partir del cliente y el inmueble."""

        cliente_name = cliente.display_name if cliente else _("Cliente")
        inmueble_name = inmueble.display_name if inmueble else _("Inmueble")
        return _("Visita de %s a %s") % (cliente_name, inmueble_name)

    def _ensure_visita_fields(self, vals, cliente_id=None, inmueble_id=None):
        """Completa `name` y `categ_ids` sólo cuando la cita es una visita."""
        vals = vals.copy()
        if not (cliente_id and inmueble_id):
            return vals

        cliente = self.env["res.partner"].browse(cliente_id)
        inmueble = self.env["inmo.inmueble"].browse(inmueble_id)

        if cliente.exists() and inmueble.exists():
            vals["name"] = self._build_visita_name(cliente, inmueble)

            categ = self.env.ref(
                "inmo_odoo.calendar_event_type_visita", raise_if_not_found=False
            )
            if categ:
                existing = set()
                if self:
                    existing = set(self.categ_ids.ids)
                vals_categ = vals.get("categ_ids")
                if vals_categ:
                    for command in vals_categ:
                        if command[0] == 6:
                            existing = set(command[2])
                        elif command[0] == 4:
                            existing.add(command[1])
                        elif command[0] == 5:
                            existing.clear()
                existing.add(categ.id)
                vals["categ_ids"] = [(6, 0, list(existing))]
        return vals

    @api.model
    def create(self, vals):
        """Antes de crear, ajusta los valores
        para que la visita quede bien identificada."""

        if vals.get("cliente_id") and vals.get("inmueble_id"):
            vals = self._ensure_visita_fields(
                vals,
                cliente_id=vals.get("cliente_id"),
                inmueble_id=vals.get("inmueble_id"),
            )
        return super().create(vals)

    def write(self, vals):
        """Si cambian cliente o inmueble, actualiza el título y la categoría."""

        if {"cliente_id", "inmueble_id"} & vals.keys() and not self.env.context.get(
            "skip_visita_autofill"
        ):
            for record in self:
                cliente_id = vals.get("cliente_id", record.cliente_id.id)
                inmueble_id = vals.get("inmueble_id", record.inmueble_id.id)
                updated_vals = record._ensure_visita_fields(
                    vals,
                    cliente_id=cliente_id,
                    inmueble_id=inmueble_id,
                )
                super(
                    VisitaInmueble, record.with_context(skip_visita_autofill=True)
                ).write(updated_vals)
            return True
        return super().write(vals)

    @api.model
    def default_get(self, fields_list):
        """Autorellena un asunto genérico en el evento de calendario
        cuando la visita se abre desde un inmueble/cliente."""

        defaults = super().default_get(fields_list)
        ctx = self.env.context
        if (
            "name" in fields_list
            and not defaults.get("name")
            and (ctx.get("default_inmueble_id") or ctx.get("default_cliente_id"))
        ):
            defaults["name"] = _("Visita inmobiliaria")
        return defaults

    @api.constrains("cliente_id", "inmueble_id")
    def _check_visita_pairs(self):
        """Exige que cliente e inmueble se informen juntos en las visitas."""
        for record in self:
            if bool(record.cliente_id) != bool(record.inmueble_id):
                raise ValidationError(
                    _("Debe indicar cliente e inmueble a la vez para una visita.")
                )
