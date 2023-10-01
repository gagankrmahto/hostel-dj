from django.contrib import admin
from .models import Room, Hostel, Booking, RoomImage, HostelImage

admin.site.disable_action('delete_selected')

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 2


class HostelImageInline(admin.TabularInline):
    model = HostelImage
    extra = 2


class RoomAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Room Details', {'fields': ['room_number', 'house_type']}),
        ('Info', {'fields': ['price', 'hostel', 'available']})
    ]

    list_display = ['room_number', 'hostel', 'house_type', 'price', 'available']
    list_filter = ['house_type', ]
    search_fields = ['house_type', 'price', 'room_number', ]
    inlines = (RoomImageInline,)


class HostelAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Hostel Details', {'fields': ['name', 'address', 'city', 'price_range']}),
        ('Info', {'fields': ['water', 'electricity','wifi','girls_hostel','boys_hostel']})
    ]
    list_display = ['name', 'city', 'all_rooms']
    list_filter = ['city',]
    search_fields = ['city', 'address', 'name']
    inlines = (HostelImageInline,)


class BookingAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Customer Information', {'fields': ['name', 'phone_number']}),
        ('Order Details', {'fields': ['room']})
    ]
    list_display = ['name', 'phone_number', 'room']


admin.site.register(Room, RoomAdmin)
admin.site.register(Hostel, HostelAdmin)
admin.site.register(Booking, BookingAdmin)