from django.shortcuts import render
from django.http import HttpResponse
import pandas as pds
import numpy as np
import os
import os.path as osp
from importlib import import_module

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '../monprojet.settings') 
django.setup()

from app1.models import Employee,Emailadress,Mail,To,Cc


def home(request):
    return render(request,"Accueil.html")

def help(request):
    response = HttpResponse()
    response.write("<h1>Explications</h1>")
    response.write("<p>Ce site est une ébauche d'une page web crée avec Django dans dans le cadre du projet de l'UE Base de données relationnelles.</p>")
    response.write("<p>Si vous voyez ce message cela signifie que cet exercice est un succés.</p>")
    return response



def tableau(request,tableau) :
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[[tableau.index[i]]+list(M[i,:]) for i in range(nrow)]
    return render(request,'Resultat_requete.html',
        {
            'index' : tableau.index,
            'columns' : tableau.columns,
            'L' : ntableau
                  })
    
def extableau(request) :
    famille=pds.DataFrame({'maman':[4,1],'papa':[7,9],'enfant':["bonjour","aurevoir"]})
    return(tableau(request,famille))
    
    
# def extableau2(request) :
#     tableau=pds.read_csv("recherchemot.csv",index_col=(0))
#     p=list(tableau.columns).index('path')+2 #rang de la colonne "path"
#     nrow=tableau.shape[0]
#     M=np.asarray(tableau)
#     ntableau=[[tableau.index[i]]+list(M[i,:]) for i in range(nrow)]
#     return render(request,'extableau2.html',
#         {
#             'index' : tableau.index,
#             'columns' : tableau.columns,
#             'L' : ntableau,
#             'p' : p
#                   })


from app1.requetes.reqtest import extableau2

def vextableau2(request) :
    return extableau2(request)


#### Requête 1 ####

from app1.requetes.Req_1 import req1

def form1(request) :
    return render(request,'req1/form1.html')

def form1bis(request) : 
    rP=request.POST
    if rP['rep1']=='0' : return req1(request,'allemployee')
    if rP['rep1']=='1' : return render(request,'req1/form1employee.html')
    if rP['rep1']=='2' : return render(request,'req1/form1adresse.html')
    
def req1employee(request) : return req1(request,'byauthor')    
def req1am(request) : return req1(request)  
    

#### Requête 2 ####
def form2(request) :
    return render(request,'form2.html')

from app1.requetes.Req_2 import req2


#### Requête 3 ####
def form3(request) :
    return render(request,'form3.html')

from app1.requetes.Req_3 import req3


#### Requête 4 ####
def form4(request) :
    return render(request,'form4.html')

from app1.requetes.Req_4 import req4


#### Requête 5 ####
def form5(request) :
    return render(request,'form5.html')

from app1.requetes.Req_5 import req5


#### Requête 6 ####
def form6(request) :
    return render(request,'form6.html')

from app1.requetes.Req_6 import req6


#### Requête 7 ####
def form7(request) :
    return render(request,'form7.html')

from app1.requetes.Req_7 import req7


#### Ouvreur de mail ####

def ouvmail(request,capture) : 
    response = HttpResponse()
    path=osp.join(os.getcwd(),'..',capture)
    k=1
    try : 
        with open(path,"r") as file :
            for ligne in file : 
                response.write('<p>'+f'{k}|'+ligne+'</p>')
                k+=1
    except UnicodeDecodeError :
        with open(path,"rb") as file :
            Lignes=str(file.read()).split(r'\n')
            for ligne in Lignes : 
                response.write('<p>'+f'{k}|'+ligne+'</p>')
                k+=1
    return response
    
#### Test pour les formulaires ####
def form(request) : 
    return render(request,'form.html')

def URL_de_reception(request) : 
    rP=request.POST
    print(rP["pays"]=="espagne",rP["pays2"]=="espagne")
    response = HttpResponse()
    response.write(f"<p>{rP}</p>")
    return response



