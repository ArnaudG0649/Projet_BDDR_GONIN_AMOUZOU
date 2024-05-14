from django.urls import path,re_path
from . import views



urlpatterns = [
    path('help', views.help, name='help'), 
    path('home', views.home, name='home'),
    path('', views.home, name='vide'), 
    path('extableau',views.extableau,name='extableau'),
    path('extableau2',views.vextableau2,name='extableau2'),
    
    re_path(r'^(maildir/.*)$', views.ouvmail, name='ouvmail'),
    
    ##Requête 1##
    path('form1',views.form1,name='form1'),
    path('form1bis',views.form1bis,name='form1bis'),

    path('req1employee',views.req1employee,name='req1employee'),
    path('req1am',views.req1am,name='req1am'),
    path('req1',views.req1,name='req1'),
    
    ##Requête 2##
    path('form2',views.form2,name='form2'),
    path('req2',views.req2,name='req2'),
    
    ##Requête 3##
    path('form3',views.form3,name='form3'),
    path('req3',views.req3,name='req3'),
    
    ##Requête 4##
    path('form4',views.form4,name='form4'),
    path('req4',views.req4,name='req4'),
    
    ##Requête 5##
    path('form5',views.form5,name='form5'),
    path('req5',views.req5,name='req5'),
    
    ##Requête 6##
    # path('form6',views.form6,name='form6'),
    path('req6',views.req6,name='req6'),    
    
    ##Juste des test##
    path('form',views.form,name='form'),
    path('URL_de_reception',views.URL_de_reception,name='URL_de_reception')
] 
