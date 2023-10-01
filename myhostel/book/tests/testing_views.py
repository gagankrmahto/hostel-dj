from django.test import TestCase, tag
from django.urls import reverse

from book.models import Hostel, Room

@tag('basic-book-views')
class BookViewsTestCase(TestCase):

    # home view
    @tag('home')
    def test_home(self):
        # return 200
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')

    @tag('staff-home')
    def test_home_staff(self):
        # return 404
        response = self.client.get(reverse('staff'))
        self.assertEqual(response.status_code, 404)

    @tag('specify')
    def test_specify(self):
        # 200 + a 302 for post
        response = self.client.get(reverse('specify'))
        self.assertEqual(response.status_code, 200)


# higher views
@tag('advanced-views')
class BookingTestCase(TestCase):
    def setUp(self):
        self.hostel_1 = Hostel(
            name='The Crud',
            location='Uplands, Limuru, Kiambu',
            city='St. Paul\'s University Main Campus',
            price_range='KSH 4500 - KSH 6000',
            distance_from_admin='5000',
            water=True,
            electricity=False
        )
        self.hostel_1.save()
        self.hostel_2 = Hostel(
            name='Mary',
            location='Skia, Ruiru, Kiambu',
            city='Kenyatta University Ruiru Campus',
            price_range='KSH 5000 - KSH 8000',
            distance_from_admin='4000',
            water=True,
            electricity=False
        )
        self.hostel_2.save()
        self.hostel_3 = Hostel(
            name='The Third',
            location='Ki, Kisauni, Mombasa',
            city='St. Paul\'s University Coast Campus',
            price_range='KSH 3000 - KSH 6000',
            distance_from_admin='5000',
            water=True,
            electricity=False
        )
        self.hostel_3.save()
        self.hostel_4 = Hostel(
            name='Triper',
            location='Uplands, Limuru, Kiambu',
            city='St. Paul\'s University Main Campus',
            price_range='KSH 2500 - KSH 4000',
            distance_from_admin='6000',
            water=True,
            electricity=False
        )
        self.hostel_4.save()
        self.hostel_5 = Hostel(
            name='5th',
            location='Githurai 44, Nairobi',
            city='KCA Main Campus',
            price_range='KSH 7000 - KSH 19000',
            distance_from_admin='400',
            water=True,
            electricity=False
        )
        self.hostel_5.save()
        self.hostel_6 = Hostel(
            name='Kremlin',
            location='Uplands, Limuru, Kiambu',
            city='St. Paul\'s University Main Campus',
            price_range='KSH 10000 - KSH 16000',
            distance_from_admin='800',
            water=True,
            electricity=False
        )
        self.hostel_6.save()
        self.room_1 = Room(
            room_number='cr-1',
            house_type='BS',
            price='5000',
            hostel=self.hostel_1
        )
        self.room_2 = Room(
            room_number='cr-2',
            house_type='BS',
            price='5000',
            hostel=self.hostel_1
        )
        self.room_3 = Room(
            room_number='cr-3',
            house_type='BS',
            price='5000',
            hostel=self.hostel_1
        )
        self.room_1.save()
        self.room_2.save()
        self.room_3.save()
        self.room_4 = Room(
            room_number='mr-1',
            house_type='BS',
            price='5000',
            hostel=self.hostel_2
        )
        self.room_5 = Room(
            room_number='mr-2',
            house_type='BS',
            price='5000',
            hostel=self.hostel_2
        )
        self.room_4.save()
        self.room_5.save()
        self.room_6 = Room(
            room_number='3-1',
            house_type='BS',
            price='5000',
            hostel=self.hostel_3
        )
        self.room_7 = Room(
            room_number='3-2',
            house_type='BS',
            price='5000',
            hostel=self.hostel_3
        )
        self.room_8 = Room(
            room_number='3-3',
            house_type='BS',
            price='5000',
            hostel=self.hostel_3
        )
        self.room_6.save()
        self.room_7.save()
        self.room_8.save()
        self.room_9 = Room(
            room_number='tr-1',
            house_type='BS',
            price='5000',
            hostel=self.hostel_4
        )
        self.room_10 = Room(
            room_number='tr-2',
            house_type='BS',
            price='5000',
            hostel=self.hostel_4
        )
        self.room_11 = Room(
            room_number='tr-3',
            house_type='BS',
            price='5000',
            hostel=self.hostel_4
        )
        self.room_9.save()
        self.room_10.save()
        self.room_11.save()


    @tag('index')
    def test_hostel_index(self):
        response = self.client.get(reverse('book:index'))
        # return 200
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book/hostel_list.html')
        # no hostels with unavailable rooms
        self.assertNotContains(response, self.hostel_5.name)
        self.assertContains(response, self.hostel_1.name)

    @tag('hostel')
    def test_hostel_detail(self):
        # return 200
        response = self.client.get(self.hostel_1.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book/hostel_detail.html')

    @tag('room-detail')
    def test_room_detail(self):
        # return 200
        response = self.client.get(self.room_3.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    @tag('book')
    def test_book(self):
        data = {
            'name': 'Tester',
            'phone_number': '0787277823'
        }
        url = self.room_3.booking_url()
        original_rooms = self.room_3.hostel.available_rooms
        original_rooms_bs = self.room_3.hostel.available_rooms
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book/now.html')

        # post
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book/success_booking.html')

        # get the same url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # the hostel should have one less avaliable room and on less available room of that type
        hostel = Hostel.objects.get(pk=self.room_3.pk)
        self.assertEqual(hostel.available_rooms, original_rooms)
        self.assertEqual(hostel.bs, original_rooms_bs)
