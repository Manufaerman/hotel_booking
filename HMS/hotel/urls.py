from django.urls import path
from .views import BookingList, RoomListView, BookingView, RoomDetailView


app_name = 'hotel'

urlpatterns = [

    path('room_list/', RoomListView, name='roomlist'),
    path('booking_list/', BookingList.as_view(), name='bookinglist'),
    path('book/', BookingView.as_view(), name='bookingview'),
    path('room/<category>', RoomDetailView.as_view(), name='roomdetailview'),


]