from django.urls import path
from .views import BookingList, RoomList, BookingView


app_name = 'hotel'

urlpatterns = [
    path('room_list/', RoomList.as_view(), name='roomlist'),
    path('booking_list/', BookingList.as_view(), name='bookinglist'),
    path('book/', BookingView.as_view(), name='bookingview')

]