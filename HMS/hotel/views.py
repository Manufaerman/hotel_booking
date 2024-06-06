from django.contrib.auth.decorators import login_required
from django.http import request
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, HttpResponse
from django.views.generic import ListView, FormView, View, DeleteView
from .models import Room, Booking, Price
from .forms import AvailibilityForm, AddBooking
from .booking_functions.availability import check_availability
from .booking_functions.get_room_list import get_room_list
from .booking_functions.calculates_everithing import CalculatesAll
from .booking_functions.save_many_prices import save_price


@login_required
def home(request):
    return render(request, 'home.html')


def roomlistview(request):

    room = Room.objects.all()
    room_list = get_room_list()
    calculos = CalculatesAll()
    calculadora = calculos.current_month_bookings()
    cleanings = calculos.number_bookings_current_month()
    form = AddBooking()
    context = {'room': room,
               'room_list': room_list,
               'calculadora': calculadora,
               'cleanings': cleanings,
               'form': form, }

    if request.method == 'POST':
        form = AddBooking(request.POST)
        if form.is_valid():
            post = True
            data = form.cleaned_data
            print(data['name'])
            room = Room.objects.filter(id=data['name'])[0]
            if check_availability(room, data['check_in'], data['check_out']):

                price = save_price(data['check_in'], data['check_out'], 80)

                booking = Booking.objects.create(
                    user=request.user,
                    room=room,
                    price=Price.objects.filter(day=''),
                    check_in=data['check_in'],
                    check_out=data['check_out']
                )
                booking.save()

                context = {'post': post,
                           'booking': booking,
                           'price': price}
                return render(request, 'room_list_view.html', context)
            else:
                no_room = True
                context = {'no_room': no_room}
                return render(request, 'room_list_view.html', context)
    return render(request, 'room_list_view.html', context)


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


