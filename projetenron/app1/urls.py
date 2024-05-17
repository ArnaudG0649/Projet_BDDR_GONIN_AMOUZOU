from django.urls import path,re_path
from . import views



urlpatterns = [    
    ##Pour ouvrir un mail##
    re_path(r'^(maildir/.*)$', views.ouvmail, name='ouvmail'),
    
    ##Page d'accueil##
    path('',views.home,name='home'),
    path('Accueil',views.home,name='home'),
    
    ##Requête 1##
    path('Formulaire1',views.form1,name='form1'),
    path('Formulaire1bis',views.form1bis,name='form1bis'),

    path('req1employee',views.req1employee,name='req1employee'),
    path('req1am',views.req1am,name='req1am'),
    path('req1',views.req1,name='req1'),
    
    ##Requête 2##
    path('Formulaire2',views.form2,name='form2'),
    path('req2',views.req2,name='req2'),
    
    ##Requête 3##
    path('Formulaire3',views.form3,name='form3'),
    path('req3',views.req3,name='req3'),
    
    ##Requête 4##
    path('Formulaire4',views.form4,name='form4'),
    path('req4',views.req4,name='req4'),
    
    ##Requête 5##
    path('Formulaire5',views.form5,name='form5'),
    path('req5',views.req5,name='req5'),
    
    ##Requête 6##
    path('Formulaire6',views.form6,name='form6'),
    path('req6',views.req6,name='req6'),

    ##Requête 7##
    path('Formulaire7',views.form7,name='form7'),
    path('req7',views.req7,name='req7'),    
    
] 
