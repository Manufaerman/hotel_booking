from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from hotel.sitemaps import StaticViewSitemap

from .views import (
    CancelarProcesoFormalizacionView,
    ConfirmarFormalizacionView,
    CrearProcesoFormalizacionView,
    DescargarContratoFormalizacionView,
    DetalleProcesoFormalizacionView,
    FormalizacionPublicaView,
    NewContractView,
    chart_data,
    contacto,
    contrato_pdf,
    contratos,
    dashboard,
    eliminar_contrato,
    finalizar_contrato,
    flat_detail,
    habitaciones,
    habitaciones_all,
    habitaciones_dashboard,
    home,
    modificar_contrato,
    modificar_inquilino,
    visitas_view, EliminarProcesoFormalizacionView, EditarProcesoFormalizacionView,
)


app_name = "hotel"


sitemaps = {
    "static": StaticViewSitemap,
}


urlpatterns = [
    # SEO

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain",
        ),
        name="robots_txt",
    ),

    # Web pública

    path(
        "",
        home,
        name="home",
    ),

    path(
        "flat/<int:id>",
        flat_detail,
        name="flat",
    ),

    path(
        "habitaciones_all/",
        habitaciones_all,
        name="habitaciones_all",
    ),

    path(
        "habitaciones/<int:id>",
        habitaciones,
        name="habitaciones",
    ),

    path(
        "contacto/",
        contacto,
        name="contacto",
    ),

    # Dashboard

    path(
        "dashboard/",
        dashboard,
        name="dashboard",
    ),

    path(
        "dashboard/chart-data/",
        chart_data,
        name="dashboard_chart_data",
    ),

    path(
        "visitas/",
        visitas_view,
        name="visitas",
    ),

    path(
        "habitaciones_dashboard/",
        habitaciones_dashboard,
        name="habitaciones_dashboard",
    ),

    # Contratos

    path(
        "contratos/",
        contratos,
        name="contratos",
    ),

    path(
        "contratos/newcontract",
        NewContractView.as_view(),
        name="newcontract",
    ),

    path(
        "contratos/<int:contrato_id>/pdf/",
        contrato_pdf,
        name="contrato_pdf",
    ),

    path(
        "contratos/<int:id>/finalizar",
        finalizar_contrato,
        name="finalizar_contrato",
    ),

    path(
        "contratos/<int:id>/modificar",
        modificar_contrato,
        name="modificar_contrato",
    ),

    path(
        "contratos/<int:id>/eliminar/",
        eliminar_contrato,
        name="eliminar_contrato",
    ),

    path(
        "contratos/modificar_inquilino/<int:id>/<int:contrato_id>",
        modificar_inquilino,
        name="modificar_inquilino",
    ),

    # Gestión interna de la formalización

    path(
        "habitaciones/<int:habitacion_id>/crear-formalizacion/",
        CrearProcesoFormalizacionView.as_view(),
        name="crear_proceso_formalizacion",
    ),

    path(
        "formalizaciones/<int:pk>/",
        DetalleProcesoFormalizacionView.as_view(),
        name="detalle_proceso_formalizacion",
    ),

    path(
        "formalizaciones/<int:pk>/cancelar/",
        CancelarProcesoFormalizacionView.as_view(),
        name="cancelar_proceso_formalizacion",
    ),

    path(
        "formalizaciones/<int:pk>/confirmar/",
        ConfirmarFormalizacionView.as_view(),
        name="confirmar_formalizacion",
    ),

    # Acceso público mediante token

    path(
        "formalizacion/<uuid:token>/",
        FormalizacionPublicaView.as_view(),
        name="formalizacion_publica",
    ),

    path(
        "formalizacion/<uuid:token>/descargar/",
        DescargarContratoFormalizacionView.as_view(),
        name="descargar_contrato_formalizacion",
    ),

    path(
        "formalizacion/<uuid:token>/",
        FormalizacionPublicaView.as_view(),
        name="formalizacion_publica",
    ),

    path(
        "formalizaciones/<int:pk>/eliminar/",
        EliminarProcesoFormalizacionView.as_view(),
        name="eliminar_proceso_formalizacion",
    ),

    path(
        "formalizaciones/<int:pk>/editar/",
        EditarProcesoFormalizacionView.as_view(),
        name="editar_proceso_formalizacion",
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )