from urllib.parse import urlencode

from django.urls import (
    NoReverseMatch,
    reverse,
)


def _reverse(nombre):
    try:
        return reverse(nombre)

    except NoReverseMatch:
        return ""


def dashboard_location(request):
    resolver_match = getattr(
        request,
        "resolver_match",
        None,
    )

    view_name = (
        resolver_match.view_name
        if resolver_match
        else ""
    )

    dashboard_url = _reverse(
        "hotel:dashboard"
    )

    gastos_url = _reverse(
        "hotel:gastos_dashboard"
    )

    proyectos_url = _reverse(
        "hotel:proyectos_dashboard"
    )

    crear_gasto_url = _reverse(
        "hotel:crear_gasto"
    )

    crear_proyecto_url = _reverse(
        "hotel:crear_proyecto"
    )


    configuraciones = {
        # ==============================================
        # DASHBOARD PRINCIPAL
        # ==============================================

        "hotel:dashboard": {
            "mostrar": False,
        },


        # ==============================================
        # GASTOS
        # ==============================================

        "hotel:gastos_dashboard": {
            "seccion": "Gastos",
            "seccion_url": "",
            "actual": "",
            "nota": "Control financiero",
            "accion_url": crear_gasto_url,
            "accion_label": "Añadir gasto",
            "mantener_contexto": True,
        },

        "hotel:crear_gasto": {
            "seccion": "Gastos",
            "seccion_url": gastos_url,
            "actual": "Nuevo gasto",
            "nota": "Registrar movimiento",
            "accion_url": "",
            "accion_label": "",
        },

        "hotel:editar_gasto": {
            "seccion": "Gastos",
            "seccion_url": gastos_url,
            "actual": "Editar",
            "nota": "Modificar movimiento",
            "accion_url": "",
            "accion_label": "",
        },


        # ==============================================
        # PROYECTOS
        # ==============================================

        "hotel:proyectos_dashboard": {
            "seccion": "Proyectos",
            "seccion_url": "",
            "actual": "",
            "nota": "Planificación y seguimiento",
            "accion_url": crear_proyecto_url,
            "accion_label": "Añadir proyecto",
        },

        "hotel:crear_proyecto": {
            "seccion": "Proyectos",
            "seccion_url": proyectos_url,
            "actual": "Nuevo proyecto",
            "nota": "Crear proyecto",
            "accion_url": "",
            "accion_label": "",
        },

        "hotel:editar_proyecto": {
            "seccion": "Proyectos",
            "seccion_url": proyectos_url,
            "actual": "Editar",
            "nota": "Modificar proyecto",
            "accion_url": "",
            "accion_label": "",
        },
    }


    configuracion = configuraciones.get(
        view_name
    )

    if not configuracion:
        return {
            "dashboard_location": {
                "mostrar": False,
            },
        }


    if not configuracion.get(
        "mostrar",
        True,
    ):
        return {
            "dashboard_location": {
                "mostrar": False,
            },
        }


    accion_url = configuracion.get(
        "accion_url",
        "",
    )


    # Conserva España/Argentina y Fedora al crear un gasto.

    if (
        accion_url
        and configuracion.get(
            "mantener_contexto",
            False,
        )
    ):
        parametros = {}

        pais = request.GET.get(
            "pais"
        )

        proyecto = request.GET.get(
            "proyecto"
        )

        if pais in {
            "ES",
            "AR",
        }:
            parametros["pais"] = pais

        if proyecto:
            parametros["proyecto"] = proyecto

        if parametros:
            accion_url = (
                f"{accion_url}?"
                f"{urlencode(parametros)}"
            )


    return {
        "dashboard_location": {
            "mostrar": True,
            "dashboard_url": dashboard_url,
            "seccion": configuracion.get(
                "seccion",
                "",
            ),
            "seccion_url": configuracion.get(
                "seccion_url",
                "",
            ),
            "actual": configuracion.get(
                "actual",
                "",
            ),
            "nota": configuracion.get(
                "nota",
                "",
            ),
            "accion_url": accion_url,
            "accion_label": configuracion.get(
                "accion_label",
                "",
            ),
        },
    }