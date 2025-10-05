from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestVisitaInmueble(TransactionCase):
    """Verifica los flujos principales del modelo VisitaInmueble."""

    @classmethod
    def setUpClass(cls):
        """Prepara datos mínimos: inmueble, clientes y fechas."""
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.inmueble_model = cls.env["inmo.inmueble"]
        cls.event_model = cls.env["calendar.event"]

        cls.partner = cls.partner_model.create({"name": "Ana Cliente"})
        cls.partner_alt = cls.partner_model.create({"name": "Luis Comprador"})
        cls.inmueble = cls.inmueble_model.create(
            {
                "nombre": "Chalet demo",
                "estado": "disponible",
            }
        )

        cls.start = fields.Datetime.now()
        cls.stop = cls.start + timedelta(hours=1)
        cls.category = cls.env.ref("inmo_odoo.calendar_event_type_visita")

    @property
    def visita_model(self):
        """Devuelve el modelo heredado que incorpora la logica de visitas."""
        return self.event_model

    def _create_visita(self, cliente=None, inmueble=None):
        """Atajo para crear visitas con los valores obligatorios."""
        return self.visita_model.create(
            {
                "cliente_id": (cliente or self.partner).id,
                "inmueble_id": (inmueble or self.inmueble).id,
                "start": self.start,
                "stop": self.stop,
            }
        )

    def test_create_autocompleta_nombre_y_categoria(self):
        """Crear una visita debe fijar el asunto y la categoría de agenda."""
        visita = self._create_visita()

        self.assertEqual(visita.name, "Visita de Ana Cliente a Chalet demo")
        self.assertIn(self.category, visita.categ_ids)

    def test_write_actualiza_titulo_al_cambiar_cliente(self):
        """Modificar cliente/inmueble debe regenerar el título."""
        visita = self._create_visita()
        visita.write({"cliente_id": self.partner_alt.id})

        self.assertEqual(visita.name, "Visita de Luis Comprador a Chalet demo")
        self.assertIn(self.category, visita.categ_ids)

    def test_constraint_exige_cliente_e_inmueble(self):
        """No se permite guardar sólo con cliente o sólo con inmueble."""
        with self.assertRaises(ValidationError):
            self.visita_model.create(
                {
                    "name": "Visita sin inmueble",
                    "cliente_id": self.partner.id,
                    "start": self.start,
                    "stop": self.stop,
                }
            )
        with self.assertRaises(ValidationError):
            self.visita_model.create(
                {
                    "name": "Visita sin cliente",
                    "inmueble_id": self.inmueble.id,
                    "start": self.start,
                    "stop": self.stop,
                }
            )

    def test_default_get_propone_nombre_generico(self):
        """Desde contexto de inmueble/cliente se propone 'Visita inmobiliaria'."""
        defaults = self.visita_model.with_context(
            default_inmueble_id=self.inmueble.id
        ).default_get(["name"])
        self.assertEqual(defaults.get("name"), "Visita inmobiliaria")
