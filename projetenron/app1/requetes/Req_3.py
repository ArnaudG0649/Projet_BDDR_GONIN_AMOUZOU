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

def req3(request) :
    rP=request.POST
    
    nature=rP["nature"]

    prenom=rP["prenom"]
    nom=rP["nom"]

    joura=rP["joura"]
    heurea=rP["heurea"]
    jourb=rP["jourb"]
    heureb=rP["heureb"]
    
    datetimea=joura+' '+heurea
    datetimeb=jourb+' '+heureb
    
    if nature=="2" : 
        
        Criteres=f"""
        Période entre {datetimea} et {datetimeb}, Nom : {nom}, Prénom : {prenom}, Employés expéditeurs et destinataires
        """
        
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT * FROM (
                SELECT emp.lastname, emp.firstname
                FROM app1_employee emp
                INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                INNER JOIN app1_mail m ON m.emailadress_id_id=ea.emailadress_id
                INNER JOIN app1_to t ON t.mail_id_id=m.mail_id
                INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=t.emailadress_id_id
                INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
                    WHERE emp2.lastname=%s AND emp2.firstname=%s AND ( m.Timedate BETWEEN %s AND %s ) 
                GROUP BY emp.firstname, emp.lastname
                ) T1
                UNION
            SELECT * FROM (
                SELECT emp.lastname, emp.firstname
                FROM app1_employee emp
                INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                INNER JOIN app1_to t ON t.emailadress_id_id=ea.emailadress_id
                INNER JOIN app1_mail m ON t.mail_id_id=m.mail_id
                INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=m.emailadress_id_id
                INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
                    WHERE emp2.lastname=%s AND emp2.firstname=%s AND ( m.Timedate BETWEEN %s AND %s) 
                GROUP BY emp.firstname, emp.lastname
                ) T2
            ORDER BY lastname
            """,[nom,prenom,datetimea,datetimeb,nom,prenom,datetimea,datetimeb])
            result=cursor.fetchall()
            columns = ["Nom","Prénom"]
    
    elif nature=="1" : 
        
        Criteres=f"""
        Période entre {datetimea} et {datetimeb}, Nom : {nom}, Prénom : {prenom}, Employés expéditeurs
        """
        
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT emp.lastname, emp.firstname
                FROM app1_employee emp
                INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                INNER JOIN app1_mail m ON m.emailadress_id_id=ea.emailadress_id
                INNER JOIN app1_to t ON t.mail_id_id=m.mail_id
                INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=t.emailadress_id_id
                INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
                    WHERE emp2.lastname= %s AND emp2.firstname= %s AND ( m.Timedate BETWEEN %s AND %s) 
                GROUP BY emp.firstname, emp.lastname
                ORDER BY lastname
            """,[nom,prenom,datetimea,datetimeb])
            result=cursor.fetchall()
            columns = ["Nom de l'expéditeur","Prénom de l'expéditeur"] 
    
    elif nature=="0" :
        
        Criteres=f"""
        Période entre {datetimea} et {datetimeb}, Nom : {nom}, Prénom : {prenom}, Employés expéditeurs
        """
        
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT emp.lastname, emp.firstname
                FROM app1_employee emp
                INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                INNER JOIN app1_to t ON t.emailadress_id_id=ea.emailadress_id
                INNER JOIN app1_mail m ON t.mail_id_id=m.mail_id
                INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=m.emailadress_id_id
                INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
                    WHERE emp2.lastname= %s AND emp2.firstname = %s AND ( m.Timedate BETWEEN %s AND %s) 
                GROUP BY emp.firstname, emp.lastname
                ORDER BY lastname
            """,[nom,prenom,datetimea,datetimeb])
            result=cursor.fetchall()
            columns = ["Nom du destinataire","Prénom du destinataire"] 

    if result==[] : 
        return HttpResponse("""<p>Aucun résultat trouvé</p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Formulaire3">Revenir au formulaire de la requête 3</a></p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Accueil">Revenir à la page d'accueil</a></p>
                            """)
    
    tableau=pds.DataFrame(result,columns=columns)
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau3.html',
        {
            'columns' : tableau.columns,
            'L' : ntableau,
            'C' : Criteres,   
            'n' : nrow})
    
