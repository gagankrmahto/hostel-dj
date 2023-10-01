import re

from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from django.db.models import Q

from .models import Hostel, Room, Booking
from .forms import BookRoomForm


class Home(generic.TemplateView):
    template_name = "home/home.html"


class Index(generic.ListView):
    model = Hostel
    context_object_name = 'hostels'
    paginate_by = 12

    def get_queryset(self):
        school = self.request.session.setdefault('school', None)
        if school:
            query_set = Hostel.objects.filter(city=school)
        else:
            query_set = Hostel.objects.all()
        return query_set.filter(all_rooms__gt=0).order_by('-available_rooms')

    def popular_hostels(self):
        # gets all popular hostels according to views it has gathered
        return self.model.objects.order_by('-views').filter(views__gt=0)[:4]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        # recent searches
        recent = self.request.session.setdefault('recent_searches', [])[-5:]
        context['recent_searches'] = list(reversed(recent))
        context['popular'] = self.popular_hostels()
        return context


class HostelDetail(generic.DetailView):
    model = Hostel
    context_object_name = 'hostel'
    slug_url_kwarg = 'slug'

    @staticmethod
    def hostel_suggestions(hostel):
        suggestions = Hostel.objects.filter(
            # suggest hostels from same school
            city__icontains=hostel.city
        ).filter(
            # all to have available rooms
            available_rooms__gt=0
        ).exclude(
            id=hostel.id
        )
        return suggestions

    def get_rooms_to_display(self):
        room_set = self.object.all_available_rooms()
        filter_by = None

        # filter the rooms according to a search result
        if 'filtered' in self.request.GET:
            filter_by = self.request.GET['filtered']

            # by house types
            house_types = {house_type[1]: house_type[0] for house_type in Room.house_types}

            if filter_by in house_types:
                room_set = room_set.filter(house_type__exact=house_types[filter_by])

            # filter by price range
            elif re.search(r'\d+-\d+', filter_by):
                prices = filter_by.split('-')
                room_set = room_set.filter(
                    price__gte=prices[0]
                ).filter(
                    price__lte=prices[1]
                )

            # filter by price below 'filter_by'
            elif re.search(r'\d{3,6}', filter_by):
                room_set = room_set.filter(price__lte=filter_by)
                filter_by = "below Ksh.%s" % filter_by

        return room_set, filter_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hostel_suggestions'] = self.hostel_suggestions(context['hostel'])
        context['rooms'], context['filtered'] = self.get_rooms_to_display()

        # add a view to the hostel using sessions. Has this user seen this hostel before?
        seen = self.request.session.setdefault('hostels_seen', [])
        if context['hostel'].pk not in seen:
            seen.append(context['hostel'].pk)
            context['hostel'].views += 1
            self.request.session['seen'] = seen
            context['hostel'].save()

        return context


class RoomDetail(View):
    @staticmethod
    def get(request, *args, **kwargs):
        room = get_object_or_404(Room, room_number=kwargs['room_number'])
        return render(request, 'book/room_detail.html', {'room': room})


class RoomBooking(View):
    template = 'book/now.html'
    form = BookRoomForm

    def get(self, request, **kwargs):
        room = get_object_or_404(Room, room_number=kwargs['room_number'])

        if not room.available:
            raise Http404

        return render(request, self.template, {
            'room': room,
            'form': self.form
        })

    def post(self, request, **kwargs):
        form = self.form(request.POST)
        room = get_object_or_404(Room, room_number=kwargs['room_number'])

        if form.is_valid():
            name = form.cleaned_data['name']
            number = form.cleaned_data['phone_number']

            if room.available:
                # create a booking instance
                Booking.objects.create(
                    room=room,
                    name=name,
                    phone_number=number
                )
                room.available = False
                room.hostel.available_rooms -= 1
                room.hostel.decrement_room_type(room.house_type)
                room.hostel.save()
                room.save()
            else:
                raise Http404("This room is not available")

        else:
            return render(request, self.template, {
                'form': form,
                'room': room
            })

        return render(request, 'book/success_booking.html', {'room': room})


# staff actions home
class StaffActions(generic.TemplateView):
    template_name = 'book/staff.html'

    def get(self, request, *args, **kwargs):
        # non staff users are get a 404 error by this page
        if not self.request.user.is_staff:
            raise Http404
        else:
            return super().get(request, args, kwargs)


# booking list
class BookingList(generic.ListView):
    model = Booking
    template_name = 'book/bookings_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        else:
            return super().get(request, args, kwargs)

    def get_queryset(self):
        return Booking.objects.order_by('cleared')


# booking detail
class BookingDetail(generic.DetailView):
    model = Booking
    template_name = "book/booking.html"
    context_object_name = 'booking'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        else:
            return super().get(request, args, kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        else:
            booking = get_object_or_404(Booking, pk=kwargs['pk'])
            booking.clear()
            messages.add_message(request, messages.INFO, 'Booking cleared')
            return redirect(reverse('booking-list'))


class BookingDelete(generic.DeleteView):
    model = Booking
    success_url = reverse_lazy('booking-list')
    template_name = 'book/booking_confirm_delete.html'


# search action
class Search(generic.TemplateView):
    template_name = 'book/search.html'

    @staticmethod
    def basic_search(query, school, **kwargs):
        # search in the name, school and address fields
        q_set = (
                Q(name__icontains=query) |
                Q(city__icontains=query) |
                Q(address__icontains=query)
        )
        query_set = kwargs.get('query_set', Hostel.objects.all())
        results = query_set.filter(q_set)

        if school:
            results = results.filter(city__contains=school)

        return results.filter(available_rooms__gt=0).order_by('-available_rooms')

    @staticmethod
    def price_search(range_of_price, school, **kwargs):
        # split the query term eg '4000-8000' as [4000, 8000] and search the price range of the hostels that
        # have price ranges between the two. Hostel class has a method to split its price range
        query_set = kwargs.get('query_set', Hostel.objects.all())
        hostels = query_set.filter(available_rooms__gt=0).order_by('-available_rooms')
        if school:
            hostels = hostels.filter(city=school)
        res = []

        if kwargs['below']:
            for hostel in hostels:
                r = hostel.get_prices()
                try:
                    new_price_range = int(range_of_price)
                except ValueError:
                    continue

                if r[0] <= new_price_range <= r[-1]:
                    res.append(hostel.pk)
        else:
            try:
                from_ = int(range_of_price.split("-")[0])
                to_ = int(range_of_price.split("-")[-1])
            except ValueError:
                from_ = 0
                to_ = 100000

            for hostel in hostels:
                r = hostel.get_prices()
                if r[0] >= from_ and r[-1] <= to_:
                    res.append(hostel.pk)

        return hostels.filter(pk__in=res)

    def advanced_search(self, query, school, **kwargs):
        query = query.split(":")
        field = query[0].upper()
        look_up = query[-1]
        term = None
        results = []

        # may be a query set is passed for chaining
        hostel_set = kwargs.get('query_set', Hostel.objects.all())

        if field in ["PRICE", "RENT", "MONTHLY", "BELOW"]:
            # price searches
            below = False
            term = 'price'
            if field == "BELOW":
                below = True
            results = self.price_search(look_up, school, below=below, query_set=hostel_set)

        elif field in ["UNIVERSITY", "CAMPUS", "SCHOOL", "COLLEGE", "city", "VARSITY", "AT"]:
            # school search
            term = 'city'
            results = hostel_set.filter(available_rooms__gt=0).filter(
                city__icontains=look_up
            ).order_by('-available_rooms')

        elif field in ["PLACE", "IN", "WHERE", "LOCATED"]:
            # address search
            term = 'address'
            results = hostel_set.filter(available_rooms__gt=0).filter(
                address__icontains=look_up
            ).order_by('-available_rooms')

            if school:
                results = results.filter(city=school)

        elif field in ["BEDROOM", "ROOM", "ROOMS"]:
            # house types
            look_up = look_up.upper()
            term = 'house_type'

            if look_up in ["ONE", "1"]:
                look_up = "One Bedroom"
                results = hostel_set.filter(one__gt=0).order_by('-one')

            elif look_up in ["TWO", "2"]:
                look_up = "Two Bedroom"
                results = hostel_set.filter(two__gt=0).order_by('-two')

            elif look_up in ["BS", "BEDSITTER"]:
                look_up = "Bedsitter"
                results = hostel_set.filter(bs__gt=0).order_by('-bs')

            elif look_up.upper() in ["SINGLE", "SINGLE ROOM"]:
                look_up = "Single Room"
                results = hostel_set.filter(sr__gt=0).order_by('-sr')

            else:
                # if none defaults to basic search
                results = []

            if school:
                results = results.filter(city__icontains=school)

        return {'results': results, 'term': term, 'look_up': look_up}

    def get(self, *args, **kwargs):
        try:
            query = self.request.GET['query']
        except MultiValueDictKeyError:
            return redirect(reverse('home'))

        advanced_search, advanced_search_term, advanced_search_look_up = False, None, None

        # retrieve previous searches
        recent = self.request.session.setdefault('recent_searches', [])
        # retrieve school
        school = self.request.session.setdefault('school', None)

        # check if the search is advanced
        if re.search(r'AND', query) or re.search(r'\w+:\w+', query):
            chains = query.split(' AND ')
            results = None

            for k, chain in enumerate(chains):
                if len(chain.split(':')) == 2:
                    advanced_search = True
                    if k == 0:
                        temp = self.advanced_search(chain, school)
                    else:
                        temp = self.advanced_search(chain, school, query_set=results)
                    results = temp['results']
                    advanced_search_term = temp['term']
                    advanced_search_look_up = temp['look_up']
                else:
                    if k == 0:
                        results = self.basic_search(chain, school)
                    else:
                        results = self.basic_search(chain, school, query_set=results)
        else:
            results = self.basic_search(query, school)

        # if the search has results it is added to session searches
        if results:
            if query in recent:
                recent.remove(query)
            recent.append(query)
            self.request.session['recent_searches'] = recent

        try:
            count = results.count()
        except TypeError:
            count = len(results)

        # pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(results, 10)

        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        return render(self.request, self.template_name, {
            'query': query,
            'results': results,
            'advanced': advanced_search,
            'advanced_field': advanced_search_term,
            'advanced_lookup': advanced_search_look_up,
            'count_results': count,
        })
