import datetime
from ..models import Booking


class CalculatesAll:

    def current_month_bookings(self):
        self.bookings = Booking.objects.all()
        date_now = datetime.datetime.now()
        self.booking_list = []
        for book in self.bookings:
            if book.check_in.month == date_now.month:
                self.booking_list.insert(0, book)


        return self.booking_list

    def number_bookings_current_month(self):
        booking = len(self.booking_list)
        total = 0
        date_now = datetime.datetime.now()
        for book in self.bookings:
            if book.check_in.month == date_now.month:
                if book.room.category == "3AC":
                    total += (12.5 * 3 )

                if book.room.category == 'TWO':
                    total += (12.5 *2)

                if book.room.category == 'ONE':
                    total += (12.5 * 2)

        return total





