from django.urls import path
from .views import BookingList, roomlistview, RoomDetailView, CancelBookingView, home


app_name = 'hotel'

urlpatterns = [

    path('room_list/', roomlistview, name='roomlist'),
    path('', home, name='home'),
    path('booking_list/', BookingList.as_view(), name='bookinglist'),
    path('room/<category>', RoomDetailView.as_view(), name='roomdetailview'),
    path('booking/cancel/<pk>', CancelBookingView.as_view(), name='cancelbookingview'),


]