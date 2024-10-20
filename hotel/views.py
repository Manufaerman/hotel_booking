from datetime import date
from django.http import JsonResponse
from django.contrib.auth.models import User
from .booking_functions.dates_functions import all_dates_between_dates
from .models import Room, Price, Booking
from django.urls import reverse_lazy
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views.generic import ListView, View, DeleteView, TemplateView
from .forms import AvailibilityForm, AddBooking
from .booking_functions.availability import check_availability, total_month_bookings, total_price_booking, \
    total_price_cleanings_current_month, total_days_book_and_not_book_current_month, booking_month_x
from .booking_functions.get_room_list import get_room_list
from .booking_functions.retrieving_data import booking_year_property, multiple_year_property, \
    booking_monthandyear_property, booking_month_allproperties, all_month_all_properties, all_month_properties_past
from django.apps import apps

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        data = {}
        data['uno'] = all_month_properties_past()

        data['dos'] = all_month_all_properties()

        data['labels'] = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        return Response(data)


def dashboard(request):
    rooms = Room.objects.all()
    if date.today().month > 9:
        mes = str(date.today().month)
        bookings = total_month_bookings(month=mes)
        cleanings = total_price_cleanings_current_month(month=mes)
        bookings2023 = booking_month_allproperties()
        usuarios = len(User.objects.all())
        return render(request, 'dashboard.html',
                      {'rooms': rooms, 'bookings': bookings, 'cleanings': cleanings, 'bookings2023': bookings2023,
                       'usuarios': usuarios})


def get_data(request, *args, **kwargs):
    data = {
        'sales': 1000,
        'customers': 10,
    }
    return JsonResponse(data)


# workers side


def roomandflats(request, id):
    print(id)
    id = get_object_or_404(Room, id=id)
    return render(request, 'room.html', {'id': id})


class DashboardBookMonth(TemplateView):
    def get(self, request, *args, **kwargs):
        month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        room = Room.objects.all()
        if kwargs:
            bookings = booking_month_x(id=kwargs['id'])
            current_room = Room.objects.get(id=kwargs['id'])
            if 'month' in kwargs:
                widget = total_days_book_and_not_book_current_month(kwargs['id'], kwargs['month'])
                return render(request, 'book_dashboard.html',
                              {'form': AddBooking(),
                               'current_room': current_room,
                               'room': room,
                               'bookings': bookings,
                               'current_month': kwargs['month'],
                               'previous_month': booking_monthandyear_property(room_id=int(kwargs['id']),
                                                                               month=kwargs['month']),
                               'month': month,
                               'widget': widget,
                               'room_list': get_room_list(),
                               'total_booking_current_month': total_month_bookings(kwargs['month']),
                               'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                               })

            # todo este else es nuevo
            else:
                if date.today().month < 10:
                    total_bill = total_month_bookings(str(date.today().month))
                    bookings = booking_month_x(id=kwargs['id'])
                    widget = total_days_book_and_not_book_current_month(kwargs['id'])
                    return render(request, 'book_dashboard.html',
                                  {'form': AddBooking(),
                                   'current_room': current_room,
                                   'room': room,
                                   'bookings': bookings,
                                   'previous_month': booking_monthandyear_property(room_id=int(kwargs['id'])),
                                   'current_month': '0' + str(date.today().month),
                                   'month': month,
                                   'widget': widget,
                                   'room_list': get_room_list(),
                                   'total_booking_current_month': total_bill,
                                   'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                                   })
                else:
                    bookings = total_month_bookings(str(date.today().month))
                    widget = total_days_book_and_not_book_current_month(kwargs['id'])
                    return render(request, 'book_dashboard.html',
                                  {'form': AddBooking(),
                                   'current_room': current_room,
                                   'room': room,
                                   'bookings': bookings,
                                   'previous_month': booking_monthandyear_property(room_id=int(kwargs['id'])),
                                   'current_month': '0' + str(date.today().month),
                                   'month': month,
                                   'widget': widget,
                                   'room_list': get_room_list(),
                                   'total_booking_current_month': bookings,
                                   'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                                   })

        else:
            if date.today().month > 9:
                mes = str(date.today().month)
                """try:"""
                return render(request, 'book_dashboard.html',
                              {'form': AddBooking(),
                               'current_room': Room.objects.get(id=1),
                               'room': room,
                               'bookings': booking_month_x('01', month=mes),
                               'previous_month': booking_monthandyear_property(room_id=1),
                               'current_month': str(date.today().month),
                               'month': month,
                               'widget': total_days_book_and_not_book_current_month(id='1', month=mes),
                               'room_list': get_room_list(),
                               'total_booking_current_month': total_month_bookings(mes),
                               'total_price_cleanings_current_month': total_price_cleanings_current_month(month=mes)
                               })

                """except:"""
                return render(request, 'nodatayet.html')

            else:
                return render(request, 'book_dashboard.html',
                              {'form': AddBooking(),
                               'current_room': Room.objects.get(id=1),
                               'room': room,
                               'bookings': booking_month_x('01'),
                               'previous_month': booking_monthandyear_property(room_id=1),
                               'current_month': '0' + str(date.today().month),
                               'month': month,
                               'widget': total_days_book_and_not_book_current_month(id='1'),
                               'room_list': get_room_list(),
                               'total_booking_current_month': total_month_bookings('0' + str(date.today().month)),
                               'total_price_cleanings_current_month': total_price_cleanings_current_month()
                               })

    def post(self, request, *args, **kwargs):
        form = AddBooking(request.POST)
        print(kwargs)
        # this instance of Room is call for the customers side.
        room = Room.objects.all()
        if form.is_valid():
            data = form.clean()
            post = True
            try:
                room = Room.objects.filter(id=kwargs['id'])[0]
            except KeyError:
                room = Room.objects.filter(id=1)[0]

            if check_availability(room, data['check_in'], data['check_out']):
                all_dates = all_dates_between_dates(data['check_in'], data['check_out'])
                user = User.objects.create_user(
                    username=data['name'] + '_' + data['last_name'],
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
                if date.today().month > 9:
                    mes = str(date.today().month)
                    context = {'post': post,
                               'id': room,
                               'booking': booking,
                               'total_booking': total_price_booking(data['check_in'], data['check_out'], data['price']),
                               'total_cleanings': total_price_cleanings_current_month(month=mes)
                               }

                    return render(request, 'home_post.html', context)
                else:
                    context = {'post': post,
                               'id': room,
                               'booking': booking,
                               'total_booking': total_price_booking(data['check_in'], data['check_out'], data['price']),
                               'total_cleanings': total_price_cleanings_current_month()
                               }

                    return render(request, 'home_post.html', context)

            else:
                no_room = True
                context = {'no_room': no_room}
                return render(request, 'home_post.html', context)

        return render(request, 'home.html', {'form': form,
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


# client side
class home(TemplateView):
    def get(self, request, *args, **kwargs):
        room = Room.objects.all()
        if kwargs:
            current_room = Room.objects.get(id=kwargs['id'])
            return render(request, 'home.html',
                          {'form': AddBooking(),
                           'current_room': current_room,
                           'room': room,
                           'room_list': get_room_list(),
                           })

        else:
            try:
                return render(request, 'home.html',
                              {'form': AddBooking(),
                               'room': room,
                               'room_list': get_room_list(),

                               })
            except IndexError:
                return render(request, 'nodatayet.html')

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

                return render(request, 'home_post.html', context)

            else:
                no_room = True
                context = {'no_room': no_room}
                return render(request, 'home_post.html', context)

        return render(request, 'home.html', {'form': form,
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


# vistas para eliminar
"""

def dashboardbook(request):
    month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    room = Room.objects.all()
    current_room = Room.objects.get(id=1)
    print(current_room.id)
    return render(request, 'book_dashboard.html',
                              {'form': AddBooking(),
                               'current_room': current_room,
                               'room': room,
                               'month': month,
                               'room_list': get_room_list(),
                               'total_booking_current_month': total_month_bookings(),
                               'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                               })
                               


class DashBoardBookFLat(TemplateView):
    def get(self, request, *args, **kwargs):
        month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        room = Room.objects.all()
        current_room = Room.objects.filter(id=1)
        if kwargs:
            bookings = booking_month_x(id=kwargs['id'])
            widget = total_days_book_and_not_book_current_month(kwargs['id'])
            current_room = Room.objects.get(id=kwargs['id'])

            return render(request, 'book_dashboard.html',
                          {'form': AddBooking(),
                           'current_room': current_room,
                            'room': room,
                           'bookings': bookings,
                           'month': month,
                           'widget': widget,
                            'room_list': get_room_list(),
                            'total_booking_current_month': total_month_bookings(),
                            'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                               })


        else:
            return render(request, 'book_dashboard.html',
                          {'form': AddBooking(),
                           'room': room,
                           'current_room': current_room,
                           'month': month,
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

                return render(request, 'home_post.html', context)

            else:
                no_room = True
                context = {'no_room': no_room}
                return render(request, 'home_post.html', context)

        return render(request, 'home.html', {'form': form,
                                                       'room': room,
                                                       'room_list': get_room_list(),
                                                       })
"""
