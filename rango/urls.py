from django.urls import path
from django.urls import re_path
from rango import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('add_category/', views.add_category, name='add_category'),
    re_path(r'^category/(?P<category_name_slug>[\w\-]+)/$',
            views.show_category, name='show_category'),
]
