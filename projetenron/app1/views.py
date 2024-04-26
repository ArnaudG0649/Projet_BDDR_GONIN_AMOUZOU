from django.shortcuts import render
from django.http import HttpResponse
import pandas as pds
import numpy as np
import os
import os.path as osp


import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '../monprojet.settings') 
django.setup()

from app1.models import Employee,Emailadress,Mail,To,Cc


def home(request):
    return HttpResponse("<p>Cette vue est une page d'accueil basique pour l'application <code>app1</code> de mon projet.</p>")

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
    
    
def extableau2(request) :
    tableau=pds.read_csv("recherchemot.csv",index_col=(0))
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[[tableau.index[i]]+list(M[i,:]) for i in range(nrow)]
    return render(request,'extableau2.html',
        {
            'index' : tableau.index,
            'columns' : tableau.columns,
            'L' : ntableau
                  })
    
def ouvmail(request,capture) : 
    response = HttpResponse()
    path=osp.join(os.getcwd(),'..',capture)
    try : 
        with open(path,"r") as file :
            for ligne in file : 
                response.write('<p>'+ligne+'</p>')
    except UnicodeDecodeError :
        with open(path,"rb") as file :
            Lignes=str(file.read()).split(r'\n')
            for ligne in Lignes : 
                response.write('<p>'+ligne+'</p>')
    return response
    

    


