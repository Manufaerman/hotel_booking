import json

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.template.loader import get_template

from .booking_functions.dates_functions import all_dates_between_dates
from .models import Room, Booking, Habitacion, Inquilino, ContratoAlquiler
from django.urls import reverse_lazy
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.views.generic import ListView, View, DeleteView, TemplateView, UpdateView
from .forms import AvailibilityForm, AddBooking, BookingForm
from .booking_functions.availability import check_availability, total_month_bookings, total_price_booking, \
    total_price_cleanings_current_month, total_days_book_and_not_book_current_month, booking_month_x
from .booking_functions.get_room_list import get_room_list
from .booking_functions.retrieving_data import \
    booking_monthandyear_property, booking_month_allproperties, all_month_all_properties, all_month_properties_past
from django.apps import apps
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
import jsonpickle


""" for the charts using jquery and js"""
class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        data = {}
        data['uno'] = all_month_properties_past()

        data['dos'] = all_month_all_properties()

        data['labels'] = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        return Response(data)

""" I will use jquery and js in order to display the bookings, show in the modals information and change the bookings"""
def kakashka(request):
    return render(request, 'kakashka.html')


class Modify(View):
    def get(selfself, request):
        data = {}
        bookings = booking_month_x(id='7', month='10')
        print(bookings)
        #data = json.dumps(list(bookings), cls=DjangoJSONEncoder)
        data = jsonpickle.encode(bookings)


        return JsonResponse(data, safe=False)



def dashboard(request):
    rooms = Room.objects.all()
    if date.today().month > 9:
        mes = date.today().month
        bookings = total_month_bookings(month=mes)
        cleanings = total_price_cleanings_current_month(month=mes)
        bookings2023 = booking_month_allproperties()
        usuarios = len(User.objects.all())
        return render(request, 'dashboard.html',
                      {'rooms': rooms, 'bookings': bookings, 'cleanings': cleanings, 'bookings2023': bookings2023,
                       'usuarios': usuarios})
    else:
        mes = date.today().month
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
            current_room = Room.objects.get(id=kwargs['id'])
            if 'month' in kwargs:
                bookings = booking_month_x(id=kwargs['id'], month=kwargs['month'])
                room_id = kwargs.get('id')
                month = kwargs.get('month', date.today().month)
                widget = total_days_book_and_not_book_current_month(room_id=room_id, month=int(month))
                return render(request, 'book_dash.html',
                              {'form': AddBooking(),
                               'current_room': current_room,
                               'room': room,
                               'bookings': bookings,
                               'current_month': kwargs['month'],
                               'previous_month': booking_monthandyear_property(room_id=int(kwargs['id']),month=kwargs['month']),
                               'month': month,
                               'widget': widget,
                               'room_list': get_room_list(),
                               'total_booking_current_month': total_month_bookings(int(kwargs['month'])),
                               'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                               })

            # todo este else es nuevo
            else:
                if date.today().month < 10:
                    total_bill = total_month_bookings(date.today().month)
                    bookings = booking_month_x(id=kwargs['id'])
                    widget = total_days_book_and_not_book_current_month(kwargs['id'])
                    return render(request, 'book_dash.html',
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
                    total_bill = total_month_bookings(date.today().month)
                    bookings = booking_month_x(id=kwargs['id'])
                    widget = total_days_book_and_not_book_current_month(kwargs['id'])
                    return render(request, 'book_dash.html',
                                  {'form': AddBooking(),
                                   'current_room': current_room,
                                   'room': room,
                                   'bookings': bookings,
                                   'previous_month': booking_monthandyear_property(room_id=int(kwargs['id'])),
                                   'current_month': str(date.today().month),
                                   'month': month,
                                   'widget': widget,
                                   'room_list': get_room_list(),
                                   'total_booking_current_month': total_bill,
                                   'total_price_cleanings_current_month': total_price_cleanings_current_month(),
                                   })

        else:
            if date.today().month > 9:
                mes = str(date.today().month)
                bookings = booking_month_x(id='7')
                """try:"""
                return render(request, 'book_dash.html',
                              {'form': AddBooking(),
                               'current_room': Room.objects.first(),
                               'room': room,
                               'bookings': bookings,
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
                bookings = booking_month_x(id="1")
                return render(request, 'book_dash.html',
                              {'form': AddBooking(),
                               'current_room': Room.objects.first(),
                               'room': room,
                               'bookings': bookings,
                               'previous_month': booking_monthandyear_property(room_id=1),
                               'current_month': '0' + str(date.today().month),
                               'month': month,
                               'widget': total_days_book_and_not_book_current_month(room_id='1', month=date.today().month),
                               'room_list': get_room_list(),
                               'total_booking_current_month': total_month_bookings(date.today().month),
                               'total_price_cleanings_current_month': total_price_cleanings_current_month()
                               })

    def post(self, request, *args, **kwargs):
        form = AddBooking(request.POST)
        print(kwargs)
        # this instance of Room is call for the customers side.
        room = Room.objects.all()
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            data = form.clean()
            print(data)
            post = True
            room_id = None

            flat = data.get('flat')

            if flat == 'tolima':
                room_id = 7

            elif flat == 'barichara':
                room_id = 8

            else:
                room_id = 9


            room = Room.objects.filter(id=room_id).first()

            print(room, 'hola')
            if room and check_availability(room, data['check_in'], data['check_out']):
                all_dates = all_dates_between_dates(data['check_in'], data['check_out'])
                if data.get('email') and not User.objects.filter(username=data['email']).exists():
                    username = data['email']
                else:
                    # Generar uno basado en el nombre y apellido
                    base_username = f"{data.get('first_name', 'anonimo')}_{data.get('last_name', 'usuario')}"
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}_{counter}"
                        counter += 1
                try:
                    user = User.objects.create_user(
                        username=username,
                        password=None,  # esto puede dar problemas
                        first_name=data['name'],
                        last_name=data['last_name'],
                        email=data['email'],
                    )
                    user.save()
                except Exception as e:
                    print("ERROR al crear usuario:", e)
                    return render(request, 'home.html', {
                        'form': form,
                        'room': room,
                        'habitaciones': Habitacion.objects.all(),
                        'room_list': get_room_list(),
                        'error_usuario': str(e)
                    })


                profile = apps.get_model('user_profile', 'UserProfile')
                profile_ = profile(user=user, phone=data['phone'])
                profile_.save()

                try:
                    booking = Booking.objects.create(
                        user=user,
                        room=room,
                        check_in=data['check_in'],
                        check_out=data['check_out'],
                        price=data['price']
                    )
                    booking.save()
                except Exception as e:
                    print("ERROR al crear reserva:", e)


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
        return HttpResponse('form is not valid or date before today')
        """return render(request, 'home.html', {'form': form,
                                             'room': room,
                                             'room_list': get_room_list(),
                                             })"""


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
        habitaciones = Habitacion.objects.all()
        if kwargs:
            current_room = Room.objects.get(id=kwargs['id'])
            return render(request, 'home.html',
                          {'form': AddBooking(),
                           'current_room': current_room,
                           'room': room,
                           'habitaciones': habitaciones,
                           'room_list': get_room_list(),
                           })

        else:
            try:
                return render(request, 'home.html',
                              {'form': AddBooking(),
                               'room': room,
                               'habitaciones': habitaciones,
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
            print(data, 'this is de data')
            post = True
            room = Room.objects.filter(namee=data['name'])[0]
            if check_availability(room, data['check_in'], data['check_out']):
                all_dates = all_dates_between_dates(data['check_in'], data['check_out'])

                booking = Booking.objects.create(
                    user=request.user,
                    room=room,
                    price=data['price'],
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
        print(room_list, 'hola soy room list')
        other_rooms = Room.objects.all
        form = AvailibilityForm()

        if len(room_list) > 0:
            room = room_list[0]
            room_category = dict(room.ROOM_CATEGORIES).get(room.category, None)
            context = {
                'room_category': room_category,
                'form': form,
                'rooms': other_rooms,
                'room':room
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


class AllBookings(ListView):
    model = Booking
    template_name = 'reservas.html'  # Usá tu template
    context_object_name = 'reservas'

    def get_queryset(self):
        return Booking.objects.all().order_by('-check_in')

class BookingUpdateView(UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'editar_reservas.html'
    success_url = reverse_lazy('hotel:reservas')

    def form_valid(self, form):
        booking = form.save(commit=False)
        if check_availability(booking.room, booking.check_in, booking.check_out):
            booking.save()
            return super().form_valid(form)
        else:
            form.add_error(None,'no hay disponibilidad para estas fechas')
            return self.form_invalid(form)

@login_required
def eliminar_reserva(request, pk):
    reserva = get_object_or_404(Booking, pk=pk)
    reserva.delete()
    return redirect('hotel:reservas')  # el nombre que uses para esa vista


def biografia(request):

    return render(request, 'biografia.html')