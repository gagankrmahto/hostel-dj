from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib import admin
from django.conf import settings
# from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from action import views as action_views
from book import views as book_views


urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # main
    path('', book_views.Home.as_view(), name='home'),

    # book/
    path('book/', include('book.urls')),

    # staff-action/add-hostel/
    path('staff-actions/', book_views.StaffActions.as_view(), name='staff'),

    # staff-actions/bookings/
    path('staff-actions/bookings/', book_views.BookingList.as_view(), name='booking-list'),

    # staff-actions/booking/4/
    path('staff-actions/bookings/<int:pk>/', book_views.BookingDetail.as_view(), name="booking"),

    # staff-actions/booking/4/delete/
    path('staff-actions/bookings/<int:pk>/delete/', book_views.BookingDelete.as_view(), name="booking-delete"),

    # specify-school/
    path('specify-city/', action_views.add_school, name="specify"),

    # un-specify-school/
    path('un-specify-city/', action_views.remove_school, name="un-specify"),

    # favicon
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL+"favicon.ico")),

    # help/
    path('help/', include('action.urls')),

]


if settings.DEBUG:
        # media  | comment out when debug is true
    # urlpatterns+=re_path('^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
    # static  | comment out when debug is true
    # urlpatterns+=re_path('^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})

    # urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT,)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)