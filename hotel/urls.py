from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import Home, BookRoomClient, \
    CancelBookingView, home, DashboardBookMonth, roomandflats, dashboard, get_data, ChartData, kakashka, Modify \
    , AllBookings, BookingUpdateView, biografia

app_name = 'hotel'

urlpatterns = [

    path('kakashka/<str:id>', roomandflats, name='roomandflats'),
    path('room_list/<id>', home.as_view(), name='roomlist'),


    path('dashboard/la/la/la/', DashboardBookMonth.as_view(), name='dashboardbookmonth'), #new
    path('dashboard/la/la/la/<id>', DashboardBookMonth.as_view(), name='dashboardbookmonth'), #new
    path('dashboard/la/la/la/<id>/<month>', DashboardBookMonth.as_view(), name='dashboardbookmonth'),
    path('reserva/eliminar/<int:pk>/', views.eliminar_reserva, name='eliminar'),
    #using it to display charts
    path('dashboard/', dashboard, name='dashboard'),
    path('api/data/', get_data, name='api_data'),
    path('api/chart/data/', ChartData.as_view()),
    path('biografia/', biografia, name='biografia'),

    #using jquery to show models in template
    path('pruebas/', kakashka, name='pruebas'),
    path('pruebas-json/', Modify.as_view(), name='pruebas-json'),

    path('booking_list/', Home.as_view(), name='bookinglist'),
    path('room/<category>', BookRoomClient.as_view(), name='roomdetailview'),
    path('booking/cancel/<pk>', CancelBookingView.as_view(), name='cancelbookingview'),
    path('', home.as_view(), name='home'),
    path('reservas/', AllBookings.as_view(), name='reservas'),
    path('reservas/editar/<int:pk>', BookingUpdateView.as_view(), name='editar')




] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)