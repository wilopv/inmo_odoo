from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestInmuebleCatastroWizard(TransactionCase):
    """Valida el comportamiento del asistente de
    Catastro inmo.inmueble.catastro.wizard."""

    @classmethod
    def setUpClass(cls):
        """Crea un inmueble base para reutilizar en cada prueba."""
        super().setUpClass()
        cls.Inmueble = cls.env["inmo.inmueble"]
        cls.Wizard = cls.env["inmo.inmueble.catastro.wizard"]

        cls.inmueble = cls.Inmueble.create(
            {
                "nombre": "Piso Demo",
                "estado": "disponible",
            }
        )

    def _new_wizard(self, referencia="8124906VK6882S0007UQ"):
        """Devuelve un asistente nuevo con el contexto esperado."""
        return self.Wizard.with_context(active_id=self.inmueble.id).create(
            {
                "inmueble_id": self.inmueble.id,
                "referencia_catastral": referencia,
            }
        )

    def test_action_confirm_updates_inmueble(self):
        """La acción debe actualizar el inmueble y cerrar el asistente."""
        wizard = self._new_wizard()

        mocked_map = {"ciudad": "Madrid", "habitaciones": 3}

        with (
            patch(
                "odoo.addons.inmo_odoo.models.catastro_service.consulta_por_referencia",
                return_value={"dummy": "value"},
            ) as consulta_mock,
            patch(
                "odoo.addons.inmo_odoo.models.catastro_service.mapear_campos_inmueble",
                return_value=mocked_map,
            ) as map_mock,
        ):
            action = wizard.action_confirm()

        consulta_mock.assert_called_once_with("8124906VK6882S0007UQ")
        map_mock.assert_called_once()
        self.assertEqual(action["type"], "ir.actions.act_window_close")

        self.inmueble.invalidate_recordset()
        self.assertEqual(self.inmueble.ciudad, "Madrid")
        self.assertEqual(self.inmueble.habitaciones, 3)

    def test_action_confirm_empty_reference_error(self):
        """Debe lanzar un error si la referencia llega vacía."""
        wizard = self._new_wizard(referencia="  ")
        with self.assertRaises(UserError):
            wizard.action_confirm()
