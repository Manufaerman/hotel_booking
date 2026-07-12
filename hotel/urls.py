from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from hotel.sitemaps import StaticViewSitemap
from . import views
from .views import dashboard, visitas_view, habitaciones, \
    NewContractView, home, flat_detail, finalizar_contrato,\
    modificar_contrato, contratos, habitaciones_dashboard, \
    modificar_inquilino, habitaciones_all, contacto, TemplateView

app_name = 'hotel'
sitemaps = {
    "static": StaticViewSitemap,
}
urlpatterns = [


    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap",),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain",), name="robots_txt"),


    #using it to display charts


    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/chart-data/', views.chart_data, name='dashboard_chart_data'),
    path('habitaciones_all/', habitaciones_all, name='habitaciones_all'),
    path('contacto/', contacto, name='contacto'),

    path('', home, name='home'),
    path('flat/<int:id>', flat_detail, name='flat'),



    path('visitas/', visitas_view, name='visitas'),
    path('habitaciones_dashboard/', habitaciones_dashboard, name='habitaciones_dashboard'),
    path('habitaciones/<int:id>', habitaciones, name='habitaciones'),


    path("contratos/", contratos, name='contratos'),
    path("contratos/<int:contrato_id>/pdf/", views.contrato_pdf, name="contrato_pdf"),
    path('contratos/newcontract', NewContractView.as_view(), name='newcontract'),

    path('contratos/<int:id>/finalizar', finalizar_contrato, name='finalizar_contrato'),
    path('contratos/<int:id>/modificar', modificar_contrato, name='modificar_contrato'),
    path('contratos/modificar_inquilino/<int:id>/<int:contrato_id>', modificar_inquilino, name='modificar_inquilino')



    ] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)