from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('evaluate/(?P<keywords>\w+?)', views.evaluate),
]
