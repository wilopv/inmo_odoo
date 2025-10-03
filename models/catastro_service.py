from __future__ import annotations

import logging
from typing import TypedDict

import requests
from odoo.api import Environment
from odoo.exceptions import UserError

from . import catastro_config as cfg

_logger = logging.getLogger(__name__)


class ResponseCatastroInmueble(TypedDict):
    referencia_catastral: str
    municipio: str
    provincia: str
    codigo_postal: str
    nombre_via: str
    superficie_m2: float
    complemento_via: str | None
    uso: str | None
    tipo_constructivo: str | None


def consulta_por_referencia(referencia: str) -> ResponseCatastroInmueble:
    """Consulta la API del Catastro y devuelve una estructura normalizada."""
    refcat = (referencia or "").strip().upper()
    if not refcat:
        raise UserError("Debe indicar una referencia catastral.")

    try:
        response = requests.get(
            cfg.CATRASTRO_URL,
            params={"RefCat": refcat},
            headers=cfg.DEFAULT_HEADERS,
            timeout=cfg.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.Timeout as err:
        _logger.exception("Timeout consultando Catastro para %s", refcat)
        raise UserError("La consulta a Catastro excedió el tiempo límite.") from err
    except requests.RequestException as err:
        _logger.exception("Error HTTP consultando Catastro para %s", refcat)
        raise UserError("No se pudo contactar con Catastro. Intente de nuevo.") from err

    data = response.json()
    if "consulta_dnprcResult" not in data:
        _logger.warning("Respuesta inesperada de Catastro: %s", data)
        raise UserError("Catastro devolvió una respuesta inesperada.")

    try:
        resultado = _normalizar_respuesta_catastro(data)
    except KeyError as err:
        _logger.warning("Estructura no reconocida en respuesta de Catastro: %s", data)
        raise UserError("Catastro devolvió una estructura no reconocida.") from err

    resultado["referencia_catastral"] = refcat
    return resultado


def mapear_campos_inmueble(
    env: Environment, data: ResponseCatastroInmueble
) -> dict[str, object]:
    """Convierte la respuesta normalizada en valores
    aptos para el modelo `inmo.inmueble`."""

    resultado: dict[str, object] = {
        "calle": data.get("nombre_via") or False,
        "calle2": data.get("complemento_via") or False,
        "codigo_postal": data.get("codigo_postal") or False,
        "ciudad": data.get("municipio") or False,
        "superficie_construida": data.get("superficie_m2", 0.0) or 0.0,
    }

    tipo_mapeado = _mapear_tipo_inmueble_desde_uso(data.get("uso"))
    if tipo_mapeado:
        resultado["tipo_inmueble"] = tipo_mapeado

    provincia_nombre = data.get("provincia")
    province = False
    if provincia_nombre:
        province = env["res.country.state"].search(
            [("name", "ilike", provincia_nombre)], limit=1
        )
    resultado["provincia"] = province.id if province else False

    country = province.country_id if province else False
    if not country:
        country = env["res.country"].search([("code", "=", "ES")], limit=1)
    resultado["id_pais"] = country.id if country else False

    # Generar el nombre comercial: TIPO_INMUEBLE + "EN" + DIRECCION
    tipo_codigo = resultado.get("tipo_inmueble")
    etiqueta_tipo = tipo_codigo or (data.get("uso") or "").lower() or "inmueble"
    via = data.get("nombre_via") or ""
    complemento = (data.get("complemento_via") or "").strip()
    direccion = via if not complemento else f"{via}, {complemento}"
    if direccion:
        resultado["nombre"] = f"{etiqueta_tipo} en {direccion}"
    else:
        resultado["nombre"] = etiqueta_tipo

    return resultado


def _normalizar_respuesta_catastro(payload: dict) -> ResponseCatastroInmueble:
    """Reduce el JSON del Catastro a un diccionario de claves legibles."""

    bi = payload["consulta_dnprcResult"]["bico"]["bi"]
    dir_urb = bi["dt"]["locs"]["lous"]["lourb"]
    dir_info = dir_urb["dir"]
    dir_int = dir_urb.get("loint", {})

    return ResponseCatastroInmueble(
        referencia_catastral="",  # Se sobreescribe tras normalizar.
        municipio=bi["dt"].get("nm", ""),
        provincia=bi["dt"].get("np", ""),
        codigo_postal=dir_urb.get("dp", ""),
        nombre_via=f"{dir_info.get('tv', '')} {dir_info.get('nv', '')}".strip(),
        complemento_via=_formatea_complemento(dir_info, dir_int) or None,
        superficie_m2=float(bi["debi"].get("sfc") or 0.0),
        uso=bi["debi"].get("luso"),
        tipo_constructivo=bi["dt"].get("cmc"),
    )


def _formatea_complemento(dir_info: dict[str, str], dir_int: dict[str, str]) -> str:
    """Construye el texto del complemento de dirección
    (portal, escalera, planta, puerta)."""

    partes = [
        f"Nº {dir_info.get('pnp')}" if dir_info.get("pnp") else "",
        f"Esc. {dir_int.get('es')}" if dir_int.get("es") else "",
        f"Pl. {dir_int.get('pt')}" if dir_int.get("pt") else "",
        f"Pu. {dir_int.get('pu')}" if dir_int.get("pu") else "",
    ]
    return " ".join(p for p in partes if p).strip()


def _mapear_tipo_inmueble_desde_uso(uso: str | None) -> str | None:
    """Convierte la etiqueta de uso catastral en el tipo del inmueble."""

    if not uso:
        return None

    uso_normalizado = uso.strip().lower()
    mapping = {
        "residencial": "piso",
        "vivienda": "piso",
        "comercial": "local",
        "local": "local",
        "industrial": "local",
        "oficina": "local",
        "garaje": "local",
        "solar": "terreno",
        "suelo": "terreno",
        "terreno": "terreno",
        "chalet": "casa",
        "unifamiliar": "casa",
        "casa": "casa",
    }

    for clave, tipo in mapping.items():
        if clave in uso_normalizado:
            return tipo

    return None
