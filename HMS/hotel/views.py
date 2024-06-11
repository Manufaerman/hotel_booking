import datetime
from time import strftime

from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, HttpResponse
from django.views.generic import ListView, FormView, View, DeleteView, TemplateView
from .models import Room, Booking, Price, Day
from .forms import AvailibilityForm, AddBooking
from .booking_functions.availability import check_availability
from .booking_functions.get_room_list import get_room_list
from .booking_functions.calculates_everithing import CalculatesAll
from .booking_functions.save_many_prices import save_price, total_actual_month_price, \
    total_previous_month_price, list_days_month, list_true_false_calendar


@login_required
def home(request):
    return render(request, 'home.html')


class RoomList(TemplateView):


    def get(self, request, *args, **kwargs):
        print(args, kwargs)
        self.template_name = 'room_list_view-html'
        room = Room.objects.all()
        # Instansiation of the class to call all the calculations functions
        calculos = CalculatesAll()
        list_true_false = list_true_false_calendar(int(kwargs['id']))
        print(list_true_false)

        return render(request, 'room_list_view.html', {'form': AddBooking(),
                            'room': room,
                            'month_days': list_days_month(),
                            'total_price_previous_month': total_previous_month_price(),
                            'total_price': total_actual_month_price(),
                            'room_list': get_room_list(),
                            'calculadora': calculos.current_month_bookings(),
                            'cleanings': calculos.number_bookings_current_month(),
                            })

    def post(self, request, *args, **kwargs):
        form = AddBooking(request.POST)
        calculos = CalculatesAll()
        #this instance of Room is call for the customers side.
        room = Room.objects.all()
        if form.is_valid():
            data = form.cleaned_data
            # is calling a function which returns a list o f true and false items wich represents
            # the booking in the month.
            list_true_false = list_true_false_calendar(int(data['name']))

            post = True
            room = Room.objects.filter(id=data['name'])[0]
            if check_availability(room, data['check_in'], data['check_out']):
                prices = save_price(data['check_in'], data['check_out'], data['price'])
                print(prices)

                for price in prices:
                    ready_to_strip = datetime.datetime.strptime(str(data['check_in']), '%Y-%m-%d')
                    day = Day.objects.create(
                        day=ready_to_strip.day,
                        month=ready_to_strip.month,
                        year=ready_to_strip.year)
                    day.save()

                for price in prices:
                    print(price.day, '---------------------------------------')
                    booking = Booking.objects.create(
                        user=request.user,
                        room=room,
                        price=Price.objects.filter(day=price.day)[0],
                        day=day,
                        check_in=data['check_in'],
                        check_out=data['check_out']
                    )
                    booking.save()
                    print(booking)
                    context = {'post': post,
                               'booking': booking,
                               'list_true_false': list_true_false,
                               }

                return render(request, 'room_list_view.html', context)

            else:
                no_room = True
                context = {'no_room': no_room}
                return render(request, 'room_list_view.html', context)

        return render(request, 'room_list_view.html', {'form': form,
                       'room': room,
                       'month_days': list_days_month(),
                       'total_price_previous_month': total_previous_month_price(),
                       'total_price': total_actual_month_price(),
                       'room_list': get_room_list(),
                       'calculadora': calculos.current_month_bookings(),
                       'cleanings': calculos.number_bookings_current_month(),
                       })



#-------------------------------------------------------------------------------------
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
        print('okkkkkk')


        if form.is_valid():
            print('yessss is valid')
            data = form.cleaned_data
            print('yessss is valid')
            available_room = []
            print(available_room)
            for room in room_list:
                if check_availability(room, data['check_in'], data['check_out']):
                    available_room.append(room)
                    print(available_room, 'this is available room ')
                if len(available_room) > 0:
                    room = available_room[0]
                    booking = Booking.objects.create(user=self.request.user,
                                                         room=room,
                                                         check_in=data['check_in'],
                                                         check_out=data['check_out'])

                    booking.save()
                    return HttpResponse(booking)
            else:
                return HttpResponse('no room available')

class CancelBookingView(DeleteView):
    model = Booking
    template_name = 'booking_cancel_view.html'
    success_url = reverse_lazy('hotel:bookinglist')


