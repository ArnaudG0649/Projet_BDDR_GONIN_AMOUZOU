from django.urls import path,re_path
from . import views



urlpatterns = [
    path('help', views.help, name='help'), 
    path('home', views.home, name='home'),
    path('', views.home, name='vide'), 
    path('extableau',views.extableau,name='extableau'),
    path('extableau2',views.vextableau2,name='extableau2'),
    re_path(r'^(maildir/.*)$', views.ouvmail, name='ouvmail'),
    path('req1',views.vreq1,name='req1')
    
] 
