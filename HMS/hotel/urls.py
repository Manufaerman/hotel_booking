from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import Home, BookRoomClient, \
    CancelBookingView, RoomList, DashBoardBook, dashboard, roomandflats

app_name = 'hotel'

urlpatterns = [

    path('kakashka/<str:id>', roomandflats, name='roomandflats'),
    path('room_list/<id>', RoomList.as_view(), name='roomlist'),
    path('dashboard/la/la/la', DashBoardBook.as_view(), name='dashboardbook'),
    path('dashboard/la/la/la/<id>', DashBoardBook.as_view(), name='dashboardbook'),
    path('dashboard/', dashboard, name='dashboard'),
    path('booking_list/', Home.as_view(), name='bookinglist'),
    path('room/<category>', BookRoomClient.as_view(), name='roomdetailview'),
    path('booking/cancel/<pk>', CancelBookingView.as_view(), name='cancelbookingview'),


    #not in use
    path('', RoomList.as_view(), name='home'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)