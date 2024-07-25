from django.contrib.auth.models import User
from .booking_functions.dates_functions import all_dates_between_dates
from .models import Room, Price
from .models import Booking
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views.generic import ListView, View, DeleteView, TemplateView, DetailView
from .forms import AvailibilityForm, AddBooking
from .booking_functions.availability import check_availability, total_month_bookings, total_price_booking, \
    total_price_cleanings_current_month, total_days_book_and_not_book_current_month, previus_month_bookings
from .booking_functions.get_room_list import get_room_list
from django.apps import apps

# workers side



def roomandflats(request, id):
    print(id)
    id = get_object_or_404(Room, id=id)
    return render(request, 'room.html', {'id': id})

def dashboard(request):
    print('hola')
    room = Room.objects.all()
    bookings = total_month_bookings()
    cleanings = total_price_cleanings_current_month()
    previus_month = previus_month_bookings()
    return render(request, 'dashboard.html', {'room': room, 'bookings': bookings, 'cleanings': cleanings, 'previus_month':previus_month})



class DashBoardBook(TemplateView):
    def get(self, request, *args, **kwargs):
        room = Room.objects.all()
        if kwargs:
            widget = total_days_book_and_not_book_current_month(kwargs['id'])
            current_room = Room.objects.get(id=kwargs['id'])

            return render(request, 'book_dashboard.html',
                          {'form': AddBooking(),
                           'current_room': current_room,
                           'room': room,
                           'widget': widget,
                           'room_list': get_room_list(),
                           'total_booking_current_month': total_month_bookings(),
                           'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                           })

        else:
            return render(request, 'book_dashboard.html',
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
                user = User.objects.create_user(
                    username=data['name']+'_'+data['last_name'],
                    password=None,
                    first_name=data['name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    )
                user.save()
                profile = apps.get_model('user_profile', 'UserProfile')
                profile_ = profile(user=user, phone=data['phone'])
                profile_.save()

                for date in all_dates:
                    price_book = Price.objects.get_or_create(room=room, price=data['price'], date_price=date)
                    price_book[0].save()

                booking = Booking.objects.create(
                    user=user,
                    room=room,
                    price=Price.objects.get(room=room, date_price=data['check_in'], price=data['price']),
                    check_in=data['check_in'],
                    check_out=data['check_out']
                )

                booking.save()

                context = {'post': post,
                           'id': room,
                           'booking': booking,
                           'total_booking': total_price_booking(data['check_in'], data['check_out'], data['price']),
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



class Home(ListView):
    model = Booking

    def get_queryset(self, *args, **kwargs):

        if self.request.user.is_staff:
            print(kwargs)
            home = Booking.objects.all()
            return home
        else:
            home = Booking.objects.filter(user=self.request.user)
            return home

#client side
class RoomList(TemplateView):

    def get(self, request, *args, **kwargs):
        room = Room.objects.all()
        if kwargs:
            current_room = Room.objects.get(id=kwargs['id'])
            return render(request, 'room_list_view.html',
                          {'form': AddBooking(),
                           'current_room': current_room,
                           'room': room,
                           'room_list': get_room_list(),
                           })

        else:
            return render(request, 'room_list_view.html',
                          {'form': AddBooking(),
                           'room': room,
                           'room_list': get_room_list(),

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



"""
cuando el cliente mira la disponibilidad da un error por que no hay precio en el 
formulario. 
"""


class BookRoomClient(View):
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

                if check_availability(room, data['check_in'], data['check_out']):
                    available_room.append(room)
                    print(available_room, 'this is available room ')
                if len(available_room) > 0:
                    room = available_room[0]
                    id_room = [str(room.id) for room in available_room]
                    print(id_room)
                    return render(request, 'available_rooms.html', {'room': available_room, 'id_room': id_room[0]})
            else:
                return HttpResponse('no room available')


class CancelBookingView(DeleteView):
    model = Booking
    template_name = 'booking_cancel_view.html'
    success_url = reverse_lazy('hotel:bookinglist')
