from django.http import request
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, HttpResponse
from django.views.generic import ListView, FormView, View, DeleteView
from .models import Room, Booking
from .forms import AvailibilityForm
from .booking_functions.availability import check_availability

def home(request):
    return render(request, 'home.html')


def roomlistview(request):
    if request.user.is_staff:
        room = Room.objects.all()
        room2 = Room.objects.all()[0]
        room_categories = dict(room2.ROOM_CATEGORIES)
        room_values = room_categories.values()
        room_list = []
        for room in room_categories:
            room2 = room_categories.get(room)
            room_url = reverse('hotel:roomdetailview', kwargs={'category': room})
            room_list.append((room2, room_url))

        context = {'room': room,
                   'room_list': room_list,
                   }
        return render(request, 'room_list_view.html', context)



class BookingList(ListView):
    model = Booking
    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_staff:
            booking_list = Booking.objects.all()
            return  booking_list
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


