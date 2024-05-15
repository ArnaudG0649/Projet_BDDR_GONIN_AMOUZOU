#!/bin/env python3

import re
import os
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

# nature="0"
# ordre="date"

# joura='2001-01-01'
# heurea='00:00'
# jourb='2100-01-01'
# heureb='00:00'


def req5(request) :
    rP=request.POST
    
    nature=rP["nature"]
    ordre=rP["ordre"]
        
    joura=rP["joura"]
    jourb=rP["jourb"]
    
    datetimea=joura
    datetimeb=jourb
    
    Criteres=f"Période entre {datetimea} et {datetimeb}"
    Criteres+=", Échanges internes-internes"*(nature=="0")+", Échanges internes-externes"*(nature=="1")
    Criteres+=", Classement par dates"*(ordre!="nb")+", Classement par nombre de mails"*(ordre=="nb")
    
    if ordre=="nb" :
        if nature=="0" : 
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM (
                    SELECT T.date, COUNT(T.mail_id) as nb FROM (
                    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
                        LEFT JOIN /*Ce LEFT JOIN a pour but de compter "0" les jours où il n'y a pas de mails correspondant à la condition sur les interners ou les externes*/
                        (SELECT m.mail_id, m.timedate FROM app1_mail m 
                            INNER JOIN 
                            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
                            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
                            GROUP BY t.mail_id_id
                            ) t ON t.mail_id_id=m.mail_id
                            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
                            WHERE aut.interne=True AND t.dest_interne=True )T0 on T0.mail_id=m.mail_id ) T
                    GROUP BY T.date ) T2
                WHERE T2.date BETWEEN %s AND %s
                ORDER BY T2.nb DESC
                """,[datetimea,datetimeb])
                result=cursor.fetchall()
                columns = ["Date","Nombre de mails échangés"]
    
        if nature=="1" : 
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM (
                    SELECT T.date, COUNT(T.mail_id) as nb FROM (
                    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
                        LEFT JOIN
                        (SELECT m.mail_id, m.timedate FROM app1_mail m 
                            INNER JOIN 
                            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
                            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
                            GROUP BY t.mail_id_id
                            ) t ON t.mail_id_id=m.mail_id
                            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
                            WHERE (aut.interne=True AND t.dest_interne=false) OR (aut.interne=False AND t.dest_interne=True) )T0 on T0.mail_id=m.mail_id ) T /*OU exclusive, au soit le destinataire ou soit l'expéditeur est interne mais pas les deux*/
                    GROUP BY T.date ) T2
                WHERE T2.date BETWEEN %s AND %s
                ORDER BY T2.nb DESC
                """,[datetimea,datetimeb])
                result=cursor.fetchall()
                columns = ["Date","Nombre de mails échangés"]
       
    
        if nature=="2" : 
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT INT_EXT.date, INT_EXT.nbint_ext as nbint_ext, INT_INT.nbint_int as nbint_int, INT_EXT.nbint_ext + INT_INT.nbint_int as Total FROM (
                SELECT COUNT(T.mail_id) as nbint_ext, T.date FROM (
                    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
                        LEFT JOIN
                        (SELECT m.mail_id, m.timedate FROM app1_mail m 
                            INNER JOIN 
                            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
                            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
                            GROUP BY t.mail_id_id
                            ) t ON t.mail_id_id=m.mail_id
                            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
                            WHERE (aut.interne=True AND t.dest_interne=false) OR (aut.interne=False AND t.dest_interne=True) )T0 on T0.mail_id=m.mail_id ) T
                    GROUP BY T.date ) INT_EXT
                INNER JOIN (
                SELECT COUNT(T.mail_id) as nbint_int, T.date FROM (
                    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
                        LEFT JOIN
                        (SELECT m.mail_id, m.timedate FROM app1_mail m 
                            INNER JOIN 
                            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
                            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
                            GROUP BY t.mail_id_id
                            ) t ON t.mail_id_id=m.mail_id
                            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
                            WHERE aut.interne=True AND t.dest_interne=True )T0 on T0.mail_id=m.mail_id ) T
                GROUP BY T.date ) INT_INT ON INT_INT.date = INT_EXT.date
                WHERE INT_EXT.date BETWEEN %s AND %s
                ORDER BY INT_EXT.nbint_ext + INT_INT.nbint_int DESC
                """,[datetimea,datetimeb])
                result=cursor.fetchall()
                columns = ["Date","Nombre de mails internes-externes échangés","Nombre de mails internes-internes échangés", "Total"]
                
    else :
        if nature=="0" : 
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM (
                    SELECT T.date, COUNT(T.mail_id) as nb FROM (
                    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
                        LEFT JOIN /*Ce LEFT JOIN a pour but de compter "0" les jours où il n'y a pas de mails correspondant à la condition sur les interners ou les externes*/
                        (SELECT m.mail_id, m.timedate FROM app1_mail m 
                            INNER JOIN 
                            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
                            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
                            GROUP BY t.mail_id_id
                            ) t ON t.mail_id_id=m.mail_id
                            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
                            WHERE aut.interne=True AND t.dest_interne=True )T0 on T0.mail_id=m.mail_id ) T
                    GROUP BY T.date ) T2
                WHERE T2.date BETWEEN %s AND %s
                ORDER BY T2.date
                """,[datetimea,datetimeb])
                result=cursor.fetchall()
                columns = ["Date","Nombre de mails échangés"]
    
        if nature=="1" : 
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM (
                    SELECT T.date, COUNT(T.mail_id) as nb FROM (
                    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
                        LEFT JOIN
                        (SELECT m.mail_id, m.timedate FROM app1_mail m 
                            INNER JOIN 
                            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
                            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
                            GROUP BY t.mail_id_id
                            ) t ON t.mail_id_id=m.mail_id
                            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
                            WHERE (aut.interne=True AND t.dest_interne=false) OR (aut.interne=False AND t.dest_interne=True) )T0 on T0.mail_id=m.mail_id ) T /*OU exclusive, au soit le destinataire ou soit l'expéditeur est interne mais pas les deux*/
                    GROUP BY T.date ) T2
                WHERE T2.date BETWEEN %s AND %s
                ORDER BY T2.date
                """,[datetimea,datetimeb])
                result=cursor.fetchall()
                columns = ["Date","Nombre de mails échangés"]
       
    
        if nature=="2" : 
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT INT_EXT.date, INT_EXT.nbint_ext as nbint_ext, INT_INT.nbint_int as nbint_int, INT_EXT.nbint_ext + INT_INT.nbint_int as Total FROM (
                SELECT COUNT(T.mail_id) as nbint_ext, T.date FROM (
                    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
                        LEFT JOIN
                        (SELECT m.mail_id, m.timedate FROM app1_mail m 
                            INNER JOIN 
                            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
                            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
                            GROUP BY t.mail_id_id
                            ) t ON t.mail_id_id=m.mail_id
                            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
                            WHERE (aut.interne=True AND t.dest_interne=false) OR (aut.interne=False AND t.dest_interne=True) )T0 on T0.mail_id=m.mail_id ) T
                    GROUP BY T.date ) INT_EXT
                INNER JOIN (
                SELECT COUNT(T.mail_id) as nbint_int, T.date FROM (
                    SELECT T0.mail_id, DATE_TRUNC('day', m.timedate) as date FROM app1_mail m 
                        LEFT JOIN
                        (SELECT m.mail_id, m.timedate FROM app1_mail m 
                            INNER JOIN 
                            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
                            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
                            GROUP BY t.mail_id_id
                            ) t ON t.mail_id_id=m.mail_id
                            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
                            WHERE aut.interne=True AND t.dest_interne=True )T0 on T0.mail_id=m.mail_id ) T
                GROUP BY T.date ) INT_INT ON INT_INT.date = INT_EXT.date
                WHERE INT_EXT.date BETWEEN %s AND %s
                ORDER BY INT_EXT.date
                """,[datetimea,datetimeb])
                result=cursor.fetchall()
                columns = ["Date","Nombre de mails internes-externes échangés","Nombre de mails internes-internes échangés", "Total"]

    if result==[] : 
        return HttpResponse("""<p>Aucun résultat trouvé</p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Formulaire5">Revenir au formulaire de la requête 5</a></p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Accueil">Revenir à la page d'accueil</a></p>
                            """)

    def foncformat(t) : return str(t)[0:10]

    tableau=pds.DataFrame(result,columns=columns)
    
    M=np.asarray(tableau)
    plt.bar(M[:,0],M[:,-1])
    plt.xticks(fontsize=6)
    plt.title("Diagramme en baton des quantités de mails échangés par jour")
    plt.xlabel('Date')
    plt.ylabel('Nombre (total) de mails')
    plt.savefig('./app1/static/Schema.png')#,dpi=300)
    
    tableau["Date"]=tableau["Date"].apply(foncformat)
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau5.html',
        {
            'columns' : tableau.columns,
            'L' : ntableau,
            'C' : Criteres })












