from .booking_functions.save_many_prices import all_dates_between_dates
from .models import Room, Price
from .models import Booking
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import render, HttpResponse
from django.views.generic import ListView, View, DeleteView, TemplateView
from .forms import AvailibilityForm, AddBooking
from .booking_functions.availability import check_availability, total_month_bookings, total_price_booking, \
    total_price_cleanings_current_month, total_days_book_and_not_book_current_month
from .booking_functions.get_room_list import get_room_list





@login_required
def home(request):
    return render(request, 'home.html')


class RoomList(TemplateView):

    def get(self, request, *args, **kwargs):
        room = Room.objects.all()

        if kwargs:
            widget = total_days_book_and_not_book_current_month(kwargs['id'])
            current_room = Room.objects.get(id=kwargs['id'])
            return render(request, 'room_list_view.html',
                          {'form': AddBooking(),
                           'current_room': current_room,
                           'room': room,
                           'widget': widget,
                           'room_list': get_room_list(),
                           'total_booking_current_month': total_month_bookings(),
                           'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                           })

        else:
            return render(request, 'room_list_view.html',
                          {'form': AddBooking(),
                            'room': room,
                            'room_list': get_room_list(),
                            'total_booking_current_month': total_month_bookings(),
                            'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                                                           })



    def post(self, request, *args, **kwargs):
        form = AddBooking(request.POST)
        # this instance of Room is call for the customers side.
        room = Room.objects.all()
        if form.is_valid():
            data = form.clean()
            post = True
            room = Room.objects.filter(id=kwargs['id'])[0]
            if check_availability(room, data['check_in'], data['check_out']):
                all_dates = all_dates_between_dates(data['check_in'], data['check_out'])
                for date in all_dates:
                    price_book = Price.objects.get_or_create(room=room, price=data['price'], date_price=date)
                    price_book[0].save()

                booking = Booking.objects.create(
                    user=request.user,
                    room=room,
                    price=Price.objects.get(room=room, date_price=data['check_in']),
                    check_in=data['check_in'],
                    check_out=data['check_out']
                )

                booking.save()

                context = {'post': post,
                           'id': room,
                           'booking': booking,
                           'total_booking': total_price_booking(data['check_in'],data['check_out'],data['price']),
                           'total_cleanings': total_price_cleanings_current_month()
                            }

                return render(request, 'room_list_view_post.html', context)

            else:
                no_room = True
                context = {'no_room': no_room}
                return render(request, 'room_list_view_post.html', context)

        return render(request, 'room_list_view.html', {'form': form,
                                                       'room': room,
                                                       'room_list': get_room_list(),
                                                       })


# -------------------------------------------------------------------------------------
class BookingList(ListView):
    model = Booking

    def get_queryset(self, *args, **kwargs):

        if self.request.user.is_staff:
            print(kwargs)
            booking_list = Booking.objects.all()
            return booking_list
        else:
            booking_list = Booking.objects.filter(user=self.request.user)
            return booking_list


class RoomDetailView(View):
    def get(self, request, *args, **kwargs):
        print(kwargs)
        room_category = self.kwargs.get('category', None)
        room_list = Room.objects.filter(category=room_category)
        print(room_list)
        form = AvailibilityForm()

        if len(room_list) > 0:
            room = room_list[0]
            room_category = dict(room.ROOM_CATEGORIES).get(room.category, None)
            context = {
                'room_category': room_category,
                'form': form,
            }
            return render(request, 'room_detail_view.html', context)
        else:
            return HttpResponse('No room available')

    def post(self, request, *args, **kwargs):
        room_category = self.kwargs.get('category', None)
        room_list = Room.objects.filter(category=room_category)
        form = AvailibilityForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            available_room = []
            for room in room_list:
                # problem with the price
                check_in = Price.objects.get_or_create(price=data['price'], fecha=data['check_in'])
                check_out = Price.objects.get_or_create(price=data['price'], fecha=data['check_out'])
                if check_availability(room, data['check_in'], data['check_out']):
                    available_room.append(room)
                    print(available_room, 'this is available room ')
                if len(available_room) > 0:
                    room = available_room[0]
                    booking = Booking.objects.get_or_create(user=self.request.user,
                                                     room=room,
                                                     check_in=check_in,
                                                     check_out=check_out,
                                                     )

                    booking.save()
                    return HttpResponse(booking)
            else:
                return HttpResponse('no room available')


class CancelBookingView(DeleteView):
    model = Booking
    template_name = 'booking_cancel_view.html'
    success_url = reverse_lazy('hotel:bookinglist')
