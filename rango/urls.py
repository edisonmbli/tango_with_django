from django.urls import path
from django.urls import re_path
from rango import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('add_category/', views.add_category, name='add_category'),
    path('restricted/', views.restricted, name='restricted'),
    path('search/', views.search, name='search'),
    path('goto/<int:page_id>/', views.track_url, name='goto'),
    path('register_profile/', views.register_profile, name='register_profile'),
    path('profile/<username>/', views.profile, name='profile'),
    path('like/', views.like_category, name='like_category'),
    path('suggest/', views.suggest_category, name='suggest_category'),
    re_path(
        r'^category/(?P<category_name_slug>[\w\-]+)/$',
        views.show_category, name='show_category'),
    re_path(
        r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$',
        views.add_page, name='add_page'),
]
