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

# prenom1='Patrice'
# nom1='Mims'

# prenom2='Debra'
# nom2='Perlingiere'

# joura='2001-01-01'
# heurea=''
# datetimea=joura+' '+heurea

# jourb='2100-01-01'
# heureb=''
# datetimeb=jourb+' '+heureb

# subject='CILCO'

def req7(request) :
    rP=request.POST
    
    prenom1=rP['prenom1']
    nom1=rP['nom1']

    prenom2=rP['prenom2']
    nom2=rP['nom2']

    joura=rP['joura']
    heurea=rP['heurea']
    datetimea=joura+' '+heurea

    jourb=rP['jourb']
    heureb=rP['heureb']
    datetimeb=jourb+' '+heureb

    subject=rP['subject']

    Criteres=f"Période entre {datetimea} et {datetimeb}, Prénom1 : {prenom1}, Nom1 : {nom1}, Prénom2 : {prenom2}, Nom2 : {nom2}"

    if subject=='' : 
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT T.subject, max(T.path) as path, T.Timedate, T.Prenom_expediteur, T.Nom_expediteur FROM
                (SELECT m.mail_id, m.subject, m.path, m.Timedate, empexp.firstname as Prenom_expediteur, empexp.lastname as Nom_expediteur FROM
                    (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_employee emp 
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    WHERE emp.firstname=%s AND emp.lastname=%s) empexp 
                    INNER JOIN app1_mail m ON m.emailadress_id_id=empexp.emailadress_id
                    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id 
                    INNER JOIN
                    (SELECT ea.emailadress_id FROM app1_employee emp 
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    WHERE emp.firstname=%s AND emp.lastname=%s) empdest ON empdest.emailadress_id=t.emailadress_id_id
                UNION
                SELECT m.mail_id, m.subject, m.path, m.Timedate, empexp.firstname as Prenom_expediteur, empexp.lastname as Nom_expediteur FROM
                    (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_employee emp 
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    WHERE emp.firstname=%s AND emp.lastname=%s) empexp 
                    INNER JOIN app1_mail m ON m.emailadress_id_id=empexp.emailadress_id
                    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id 
                    INNER JOIN
                    (SELECT ea.emailadress_id FROM app1_employee emp 
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    WHERE emp.firstname=%s AND emp.lastname=%s) empdest ON empdest.emailadress_id=t.emailadress_id_id
                ) T
                WHERE T.Timedate BETWEEN %s AND %s
                GROUP BY T.subject, T.Timedate, T.Prenom_expediteur, T.Nom_expediteur
                ORDER BY T.Timedate  
                """,[prenom1,nom1,prenom2,nom2,prenom2,nom2,prenom1,nom1,datetimea,datetimeb])            
            result=cursor.fetchall()
            
    else :
        
        Criteres+=f", Objet : {subject}"
        
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT T.subject, max(T.path) as path, T.Timedate, T.Prenom_expediteur, T.Nom_expediteur FROM
                (SELECT m.mail_id, m.subject, m.path, m.Timedate, empexp.firstname as Prenom_expediteur, empexp.lastname as Nom_expediteur FROM
                    (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_employee emp 
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    WHERE emp.firstname=%s AND emp.lastname=%s) empexp 
                    INNER JOIN app1_mail m ON m.emailadress_id_id=empexp.emailadress_id
                    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id 
                    INNER JOIN
                    (SELECT ea.emailadress_id FROM app1_employee emp 
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    WHERE emp.firstname=%s AND emp.lastname=%s) empdest ON empdest.emailadress_id=t.emailadress_id_id
                UNION
                SELECT m.mail_id, m.subject, m.path, m.Timedate, empexp.firstname as Prenom_expediteur, empexp.lastname as Nom_expediteur FROM
                    (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_employee emp 
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    WHERE emp.firstname=%s AND emp.lastname=%s) empexp 
                    INNER JOIN app1_mail m ON m.emailadress_id_id=empexp.emailadress_id
                    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id 
                    INNER JOIN
                    (SELECT ea.emailadress_id FROM app1_employee emp 
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    WHERE emp.firstname=%s AND emp.lastname=%s) empdest ON empdest.emailadress_id=t.emailadress_id_id
                ) T
                WHERE (T.Timedate BETWEEN %s AND %s) AND (T.subject LIKE %s OR T.subject LIKE %s)
                GROUP BY T.subject, T.Timedate, T.Prenom_expediteur, T.Nom_expediteur
                ORDER BY T.Timedate  
                """,[prenom1,nom1,prenom2,nom2,prenom2,nom2,prenom1,nom1,datetimea,datetimeb,r'% '+subject,subject])            
            result=cursor.fetchall()   
    
    
    if result==[] : 
        return HttpResponse("""<p>Aucun résultat trouvé</p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Formulaire7">Revenir au formulaire de la requête 7</a></p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Accueil">Revenir à la page d'accueil</a></p>
                            """)
    
    def foncformat(t) : return str(t)
    
    print(result)
    
    columns = ["Objet","Chemin d'accés (cliquez pour ouvrir)","Date","Prénom de l'auteur","Nom de l'auteur"]
    tableau=pds.DataFrame(result,columns=columns)
    tableau["Date"]=tableau["Date"].apply(foncformat)
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau7.html',
        {
        'index' : tableau.index,
        'columns' : tableau.columns,
        'L' : ntableau,
        'p' : 2,
        'C' : Criteres })
