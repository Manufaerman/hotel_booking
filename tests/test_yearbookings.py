import pytest
import asyncio
from hotel.models import Booking

@pytest.mark.asyncio
async def test_yearbookings():
    reservas = Booking.objects.all()
    return reservas
