from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError


# from jsonfield import JSONField to from django.db.models import JSONField
import re


# def sixteen_by_nine(width, height):
#     lane = width*9
#     lane = int(lane/16)
#     if lane == int(height):
#         return True
#     else:
#         return False


# hostel compound
class Hostel(models.Model):
    id = models.IntegerField(auto_created=True,primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=400, help_text='Preferred name of the premises', unique=True,)
    slug = models.SlugField(blank=True, unique=True)
    address = models.CharField(max_length=400, help_text='Where is it found')
    city = models.CharField(
        max_length=400,
        help_text='City where hostel is located',
        default="Ranchi"
    )
    available_rooms = models.IntegerField(default=0)
    all_rooms = models.IntegerField(blank=True, null=True)
    # distance_from_admin = models.IntegerField(help_text='How far is it from the administration building')
    water = models.BooleanField(default=False, help_text='Is there free water?')
    electricity = models.BooleanField(default=False, help_text='Is there free power?')
    wifi = models.BooleanField(default=False, help_text='Is there free WiFi?')
    girls_hostel = models.BooleanField(default=False, help_text='Girls Allowed ?')
    boys_hostel = models.BooleanField(default=False, help_text='Boys Allowed ?')
    wifi = models.BooleanField(default=False, help_text='Is there free WiFi?')
    price_range = models.CharField(
        max_length=300,
        blank=True,
        help_text='Enter price range in the following format \'INR 4500 - INR 6000\''
    )
    views = models.IntegerField(default=0)
    bs = models.IntegerField(default=0)
    one = models.IntegerField(default=0)
    two = models.IntegerField(default=0)
    sr = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return '{} at {}'.format(self.name, self.city)

    def clean(self):
        # the price range should be in the correct format
        if not re.search(r'INR\s\d*\s-\sINR\s\d*', str(self.price_range)):
            raise ValidationError(_('Please use the correct format for price range as described.'))

        # ranges should make sense
        ranges = str(self.price_range).split(" ")
        
        if int(ranges[1]) > int(ranges[-1]):
            raise ValidationError(_("The range starts from lowest to highest"))

        return super().clean()

    def save(self, *args, **kwargs):
        # count all rooms
        self.all_rooms = self.room_set.count()

        # slug url
        self.slug = slugify(str(self.name))
        return super().save(args, kwargs)

    def delete(self, *args, **kwargs):
        # delete all images once the hostel is deleted
        images = self.hostelimage_set.all()
        for image in images:
            image.file.delete()
        return super().delete()

    def get_main_image(self):
        try:
            img = self.hostelimage_set.filter(is_main=True)[0].file.url
        except IndexError:
            img = '/media/defaults/default_hostel.jpg'
        return img

    def get_absolute_url(self):
        return reverse('book:hostel', args=[str(self.slug)])

    def get_prices(self):
        res = str(self.price_range).split(" ")
        return [int(item) for item in res if item.isdigit()]

    def increment_room_type(self, room_type):
        room_type = str(room_type)
        if room_type == "BS":
            self.bs += 1
        elif room_type == "SR":
            self.sr += 1
        elif room_type == "1B":
            self.one += 1
        elif room_type == '2B':
            self.two += 1
        self.save()

    def decrement_room_type(self, room_type):
        room_type = str(room_type)
        if room_type == "BS":
            self.bs -= 1
        elif room_type == "SR":
            self.sr -= 1
        elif room_type == "1B":
            self.one -= 1
        elif room_type == '2B':
            self.two -= 1
        self.save()

    def all_available_rooms(self):
        return self.room_set.filter(available=True)

    def all_unavailable_rooms(self):
        return self.room_set.filter(available=False)


# rooms
class Room(models.Model):
    house_types = (('1B', 'One Bedroom'), ('2B', 'Two Bedroom'), ('BS', 'Bedsitter'), ('SR', 'Single Room'))

    room_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    price = models.PositiveIntegerField()
    house_type = models.CharField(max_length=2, choices=house_types)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)
    tallied = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return 'Room number {} a {} from {}'.format(self.room_number, self.house_type, self.hostel)

    def clean(self):
        # price should not be lower or higher than price range
        hostel_range = self.hostel.get_prices()
        if self.price < int(hostel_range[0]) or self.price > int(hostel_range[-1]):
            raise ValidationError(_(
                "Ensure price is within the price range of the \"{}\" that is between {} and {}".format(
                    self.hostel.name,
                    hostel_range[0],
                    hostel_range[-1]
                )
            ))

        return super().clean()

    def save(self, *args, **kwargs):
        if not self.tallied:
            # all available rooms
            self.hostel.available_rooms += 1
            # room types
            self.hostel.increment_room_type(self.house_type)
            # save hostel
            self.tallied = True
            self.hostel.save()
            
        return super().save(args, kwargs)

    def delete(self, *args, **kwargs):
        # delete all images once the room is deleted
        images = self.roomimage_set.all()
        self.hostel.available_rooms -= 1
        for image in images:
            image.file.delete()
        return super().delete()

    def get_main_image(self):
        try:
            img = self.roomimage_set.filter(is_main=True)[0].file.url
        except IndexError:
            img = '/media/defaults/default_room.png'
        return img

    def get_house_type(self):
        type_ = self.house_type
        if type_ == self.house_types[0][0]:
            return self.house_types[0][-1]
        elif type_ == self.house_types[1][0]:
            return self.house_types[1][-1]
        elif type_ == self.house_types[2][0]:
            return self.house_types[2][-1]
        elif type_ == self.house_types[3][0]:
            return self.house_types[3][-1]

    def get_absolute_url(self):
        return reverse('book:room', kwargs={'slug': str(self.hostel.slug), 'room_number': str(self.room_number)})

    def booking_url(self):
        return self.get_absolute_url() + 'now/'


def upload_room_to(instance, filename):
    return "hostel/{}/rooms/{}/{}".format(instance.room.hostel.slug, instance.room.room_number, filename)


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    file = models.ImageField(upload_to=upload_room_to, help_text="PLEASE CROP TO 16:9")
    is_main = models.BooleanField(default=False, help_text="PLEASE MARK ONE AS MAIN!!!!")
    objects = models.Manager()

    def __str__(self):
        return 'For {}'.format(self.room)

    def delete(self, *args, **kwargs):
        self.file.delete()
        return super().delete()

    # def clean(self):
    #     # image to be 16:9
    #     if not sixteen_by_nine(self.file.width, self.file.height):
    #         raise ValidationError(_('Image is not 16:9 please crop it'))

        # return super().clean()


def upload_hostel_to(instance, filename):
    return 'hostel/{}/images/{}'.format(instance.hostel.slug, filename)


class HostelImage(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    file = models.ImageField(upload_to=upload_hostel_to, help_text="PLEASE CROP TO 16:9")
    is_main = models.BooleanField(default=False, help_text="PLEASE MARK ONE AS MAIN!!!!")
    objects = models.Manager()

    def __str__(self):
        return 'For {}'.format(self.hostel)

    def delete(self, *args, **kwargs):
        self.file.delete()
        return super().delete()

    # def clean(self):
    #     # image to be 16:9
    #     if not sixteen_by_nine(self.file.width, self.file.height):
    #         raise ValidationError(_('Image is not 16:9 please crop it'))

    #     return super().clean()


# bookings
class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text='Enter your preferred name')
    phone_number = models.CharField(max_length=10, help_text='Enter phone number')
    cleared = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    objects = models.Manager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return 'order by {} for {}'.format(self.name, self.room)

    def delete(self, using=None, keep_parents=False):
        self.room.available = True
        self.room.hostel.available_rooms += 1
        self.room.save()
        self.room.hostel.increment_room_type(self.room.house_type)
        self.room.hostel.save()
        return super().delete()

    def clear(self):
        self.cleared = True
        self.save()

    def staff_url(self):
        return reverse('booking', args=[str(self.pk)])

    def delete_url(self):
        return reverse('booking-delete', args=[str(self.pk)])
