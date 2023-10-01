from django.test import TestCase, tag
from django.core.files import File
from django.utils.text import slugify

from mock import MagicMock

# noinspection PyUnresolvedReferences
from book.models import Hostel, Room, HostelImage, RoomImage


@tag('hostel-model')
class HostelModelTestCase(TestCase):
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
        self.image_mock = MagicMock(spec=File)
        self.image_mock.name = 'new.jpg'
        self.img_1_1 = HostelImage(
            hostel=self.hostel_1,
            file=self.image_mock,
            is_main=True
        )
        self.room_1_1 = Room(
            room_number='cr-1',
            house_type='BS',
            price='5000',
            hostel=self.hostel_1
        )
        self.img_room_1_1 = None

    @tag('basic-hostel')
    def test_rooms(self):
        # all rooms and views should be 0
        self.assertEqual(self.hostel_1.available_rooms, 0)
        self.assertEqual(self.hostel_1.views, 0)

    @tag('main-img')
    def test_main_image(self):
        # get a main image or default image
        self.assertEqual(self.hostel_1.get_main_image(), '/media/defaults/default_hostel.jpg')
        # create new hostel image and receive it instead of default
        self.img_1_1.save()
        self.assertEqual(self.hostel_1.get_main_image(), '/media/hostel/{}/images/new.jpg'.format(self.hostel_1.slug))
        self.img_1_1.delete()

    @tag('room-overall')
    def test_room_details(self):
        # hostel should have +1 rooms
        self.room_1_1.save()
        self.assertEqual(self.hostel_1.available_rooms, 1)

    @tag('hostel-slug')
    def test_hostel_slug(self):
        # make sure the slug is slug-crud
        self.assertEqual(self.hostel_1.slug, slugify(self.hostel_1.name))

    @tag('prices')
    def test_prices_range(self):
        # should return [4500, 6000]
        self.assertListEqual(self.hostel_1.get_prices(), [4500, 6000])

    @tag('url')
    def test_absolute_url(self):
        # url for hostel should be /book/hostel/the-crud/
        self.assertEqual(self.hostel_1.get_absolute_url(), '/book/hostel/the-crud/')
        # url for room should be /book/hostel/the-crud/cr-1/
        self.assertEqual(self.room_1_1.get_absolute_url(), '/book/hostel/the-crud/cr-1/')

    @tag('room-img')
    def test_room_img(self):
        # default image should be returned
        self.room_1_1.save()
        self.assertEqual(self.room_1_1.get_main_image(), '/media/defaults/default_room.png')
        self.image_mock.name = 'room.jpg'
        self.img_room_1_1 = RoomImage(
            room=self.room_1_1,
            file=self.image_mock,
            is_main=True
        )
        self.img_room_1_1.save()
        self.assertEqual(self.room_1_1.get_main_image(), '/media/hostel/{}/rooms/{}/room.jpg'.format(
            self.room_1_1.hostel.slug,
            self.room_1_1.room_number,
        ))
        self.img_room_1_1.delete()
