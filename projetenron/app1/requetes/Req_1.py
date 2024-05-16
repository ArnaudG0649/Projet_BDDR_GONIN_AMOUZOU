#!/bin/env python3

import re
import os
import os.path as osp 
import datetime as dt
import django
import matplotlib.pyplot as plt
import pandas as pds
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse


#'django_extensions' ##Pour éxecuter la commande au projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetenron.settings') 
django.setup()


from app1.models import Employee,Emailadress,Mail,To,Cc #,Re
from django.core.exceptions import ObjectDoesNotExist

from django.db import connection

def req1(request,typerep='') :
    rP=request.POST
    print(typerep)
        
    if typerep=='allemployee' : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT e.employee_id, e.lastname, e.firstname, e.category, e.mailbox, string_agg(ea.emailadress_id,' ; ')
            FROM app1_employee e
            INNER JOIN app1_emailadress ea
                ON e.employee_id=ea.employee_id_id
            GROUP BY e.employee_id, e.lastname, e.firstname, e.category, e.mailbox
            """)
            result=cursor.fetchall()
            columns = ['identifiant','nom','prénom','catégorie','boite mail', 'adresses mail'] 
            
        tableau=pds.DataFrame(result,columns=columns)
        tableau['catégorie'].fillna('Inconnue',inplace=True)
        
        nrow=tableau.shape[0]
        M=np.asarray(tableau)
        ntableau=[list(M[i,:]) for i in range(nrow)]
        Criteres='Tous les employés'
        return render(request,'tableau1.html',
            {
                'columns' : tableau.columns,
                'L' : ntableau,
                'C' : Criteres,   
                'n' : nrow})
    
    elif typerep =='byauthor' :
        prenom,nom=rP['prenom'],rP['nom']
        Criteres=f"Nom : {nom}, Prénom : {prenom}"
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT e.employee_id, e.lastname, e.firstname, e.category, e.mailbox, string_agg(ea.emailadress_id,' ; ')
            FROM app1_employee e
            INNER JOIN app1_emailadress ea
                ON e.employee_id=ea.employee_id_id
            WHERE e.lastname=%s AND e.firstname=%s
            GROUP BY e.employee_id, e.lastname, e.firstname, e.category, e.mailbox
            """,[nom,prenom])
            result=cursor.fetchall()
            columns = ['identifiant','nom','prénom','catégorie','boite mail', 'adresses mail'] 

        if result==[] : 
            return HttpResponse("""<p>Aucun résultat trouvé</p>
                                <p><a href="http://127.0.0.1:7000/Application_Projet/Formulaire1">Revenir au formulaire de la requête 1</a></p>
                                <p><a href="http://127.0.0.1:7000/Application_Projet/Accueil">Revenir à la page d'accueil</a></p>
                                """)
            
        tableau=pds.DataFrame(result,columns=columns)
        tableau['catégorie'].fillna('Inconnue',inplace=True)
        
        nrow=tableau.shape[0]
        M=np.asarray(tableau)
        ntableau=[list(M[i,:]) for i in range(nrow)]
        return render(request,'tableau1.html',
            {
                'columns' : tableau.columns,
                'L' : ntableau,
                'C' : Criteres,   
                'n' : nrow})

    else : 
        adresse=rP['adresse']
        Criteres=f"Adresse mail : {adresse}"
        
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT  e.employee_id, e.lastname , e.firstname , e.category, e.mailbox, string_agg(ea.emailadress_id,' ; ')
            FROM (SELECT * 
                FROM app1_employee e
                INNER JOIN app1_emailadress ea
                    ON e.employee_id=ea.employee_id_id
                WHERE ea.emailadress_id=%s) e
            INNER JOIN app1_emailadress ea 
                ON e.employee_id=ea.employee_id_id
            GROUP BY e.employee_id, e.firstname, e.lastname , e.category, e.mailbox
            """,[adresse])
            result=cursor.fetchall()
            columns = ['identifiant','nom','prénom','catégorie','boite mail', 'adresses mail'] 
        
        if result==[] : 
            return HttpResponse("""<p>Aucun résultat trouvé</p>
                                <p><a href="http://127.0.0.1:7000/Application_Projet/Formulaire1">Revenir au formulaire de la requête 1</a></p>
                                <p><a href="http://127.0.0.1:7000/Application_Projet/Accueil">Revenir à la page d'accueil</a></p>
                                """)
        
        tableau=pds.DataFrame(result,columns=columns)
        tableau['catégorie'].fillna('Inconnue',inplace=True)
        
        nrow=tableau.shape[0]
        M=np.asarray(tableau)
        ntableau=[list(M[i,:]) for i in range(nrow)]
        return render(request,'tableau1.html',
            {
                'columns' : tableau.columns,
                'L' : ntableau,
                'C' : Criteres,   
                'n' : nrow})



