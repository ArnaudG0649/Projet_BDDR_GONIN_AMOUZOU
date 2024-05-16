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

def req4(request) :
    rP=request.POST
    
    #"0" : a->b ; "1" : a<-b ; "2" : a<->b 
    nature=rP["nature"]
    
    prenom=rP["prenom"]
    nom=rP["nom"]
    
    nomprenom = prenom!="" and nom!=""
    
    if ((prenom!="") or (nom!="")) and not nomprenom : return HttpResponse("<p>Veuillez rentrer entièrement le nom et le prénom ou aucun des deux !</p>")
    
    joura=rP["joura"]
    heurea=rP["heurea"]
    jourb=rP["jourb"]
    heureb=rP["heureb"]
    
    datetimea=joura+' '+heurea
    datetimeb=jourb+' '+heureb
    
    minm=rP["minm"]
    
    if nomprenom :        
        if nature=="0" :
            
            Criteres=f"""
            Période entre {datetimea} et {datetimeb}, Minimum de mails : {minm}, Nom : {nom}, Prénom : {prenom}, les employés ci-dessous sont ses destinataires
            """
            
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM(
                SELECT emp.lastname, emp.firstname, COUNT(t.mail_id) as nb FROM 
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
                       ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id
                        FROM app1_to t
                        INNER JOIN app1_mail m ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2 ON m.emailadress_id_id=ea2.emailadress_id
                        INNER JOIN app1_employee emp2 ON ea2.employee_id_id=emp2.employee_id
                        WHERE emp2.lastname= %s AND emp2.firstname= %s AND ( m.Timedate BETWEEN %s AND %s)
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ORDER BY nb DESC )T
                    WHERE T.nb >= %s
                """,[nom,prenom,datetimea,datetimeb,minm])
                result=cursor.fetchall()
                columns = ["Nom du destinataire","Prénom du destinataire","Nombre de mails envoyés"]
    
    
        if nature=="1" :
            
            Criteres=f"""
            Période entre {datetimea} et {datetimeb}, Minimum de mails : {minm}, Nom : {nom}, Prénom : {prenom}, les employés ci-dessous sont ses expéditeurs
            """
            
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM(
                SELECT emp.lastname, emp.firstname, COUNT(m.mail_id) as nb FROM 
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
                       ) emp
                    LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id
                        FROM app1_mail m
                        INNER JOIN app1_to t ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2 ON t.emailadress_id_id=ea2.emailadress_id
                        INNER JOIN app1_employee emp2 ON ea2.employee_id_id=emp2.employee_id
                        WHERE emp2.lastname= %s AND emp2.firstname= %s AND ( m.Timedate BETWEEN %s AND %s)
                        ) m
                        ON m.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ORDER BY nb DESC )T
                    WHERE T.nb >= %s
                """,[nom,prenom,datetimea,datetimeb,minm])
                result=cursor.fetchall()
                columns = ["Nom de l'expéditeur","Prénom de l'expéditeur","Nombre de mails reçus"]
   

        if nature=="2" :
            
            Criteres=f"""
            Période entre {datetimea} et {datetimeb}, Minimum de mails : {minm}, Nom : {nom}, Prénom : {prenom}
            """
            
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT ENV.lastname, ENV.Firstname, nbenv, nbrec, nbenv+nbrec as total FROM  
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbenv FROM 
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
                       ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id
                        FROM app1_to t
                        INNER JOIN app1_mail m ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2 ON m.emailadress_id_id=ea2.emailadress_id
                        INNER JOIN app1_employee emp2 ON ea2.employee_id_id=emp2.employee_id
                        WHERE emp2.lastname= %s AND emp2.firstname= %s AND ( m.Timedate BETWEEN %s AND %s)
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) ENV
                INNER JOIN 
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbrec FROM 
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
                       ) emp
                    LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id
                        FROM app1_mail m
                        INNER JOIN app1_to t ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2 ON t.emailadress_id_id=ea2.emailadress_id
                        INNER JOIN app1_employee emp2 ON ea2.employee_id_id=emp2.employee_id
                        WHERE emp2.lastname= %s AND emp2.firstname= %s AND ( m.Timedate BETWEEN %s AND %s)
                        ) m
                        ON m.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) REC
                    ON ENV.employee_id = REC.employee_id
                    WHERE nbenv+nbrec >= %s
                    ORDER BY total DESC 
                """,[nom,prenom,datetimea,datetimeb,nom,prenom,datetimea,datetimeb,minm])
                result=cursor.fetchall()
                columns = ["Nom","Prénom","Nombre de mails envoyés de cette personne","Nombre de mails reçus de cette personne","Total"]
 
    else : 
        if nature=="0" :
            
            Criteres=f"""
            Période entre {datetimea} et {datetimeb}, Minimum de mails : {minm}
            """
            
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM (
                SELECT emp.firstname, emp.lastname, emp2.firstname as firstname_d, emp2.lastname as lastname_d, COUNT(m.mail_id) as nbmail
                    FROM app1_employee emp
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    INNER JOIN app1_mail m ON m.emailadress_id_id=ea.emailadress_id
                    INNER JOIN app1_to t ON t.mail_id_id=m.mail_id
                    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=t.emailadress_id_id
                    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
                        WHERE ( m.Timedate BETWEEN %s AND %s)
                    GROUP BY emp.firstname, emp.lastname, emp2.firstname, emp2.lastname 
                    ORDER BY COUNT(m.mail_id) DESC ) T
                    WHERE T.nbmail >= %s
                """,[datetimea,datetimeb,minm])
                result=cursor.fetchall()
                columns = ["Nom de l'expéditeur","Prénom de l'expéditeur","Nom du destinataire","Prénom de destinataire","Nombre de mails envoyés"]
    
    
        if nature=="1" : 
            
            Criteres=f"""
            Période entre {datetimea} et {datetimeb}, Minimum de mails : {minm}
            """
            
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT * FROM (
                SELECT emp.firstname, emp.lastname, emp2.firstname as firstname_d, emp2.lastname as lastname_d, COUNT(m.mail_id) as nbmail
                    FROM app1_employee emp
                    INNER JOIN app1_emailadress ea ON emp.employee_id=ea.employee_id_id
                    INNER JOIN app1_to t ON t.emailadress_id_id=ea.emailadress_id
                    INNER JOIN app1_mail m ON t.mail_id_id=m.mail_id
                    INNER JOIN app1_emailadress ea2 ON ea2.emailadress_id=m.emailadress_id_id
                    INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id
                        WHERE ( m.Timedate BETWEEN %s AND %s)
                    GROUP BY emp.firstname, emp.lastname, emp2.firstname, emp2.lastname
                    ORDER BY COUNT(m.mail_id) DESC ) T
                    WHERE T.nbmail >= %s   
                """,[datetimea,datetimeb,minm])
                result=cursor.fetchall()
                columns = ["Nom de l'expéditeur","Prénom de l'expéditeur","Nom du destinataire","Prénom de destinataire","Nombre de mails envoyés"]
   

        if nature=="2" :
            
            Criteres=f"""
            Période entre {datetimea} et {datetimeb}, Minimum de mails : {minm}
            """
            
            with connection.cursor() as cursor:
                cursor.execute(
                """
                SELECT empg.lastname, empg.firstname, empd.lastname, empd.firstname, T.nbgauche_droite, T.nbdroite_gauche, T.nbgauche_droite+T.nbdroite_gauche as Total FROM
                (SELECT Tdp.id_expediteur as employe1_id, Tdp.id_destinataire as employe2_id, Tdp.nbmail as nbgauche_droite, Tdp2.nbmail as nbdroite_gauche FROM
                    (SELECT m.employee_id as id_destinataire, SUM(m.nbmail) as nbmail, ea.employee_id as id_expediteur FROM
                    (SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
                        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
                    ) ea
                    INNER JOIN
                    (SELECT t.employee_id, COUNT(m.mail_id) AS nbmail, m.emailadress_id_id FROM app1_mail m 
                    RIGHT JOIN
                        (SELECT ea2.employee_id, t.mail_id_id FROM app1_to t 
                        RIGHT JOIN
                            (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
                                INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
                                ON ea2.emailadress_id=t.emailadress_id_id 
                        ) t ON t.mail_id_id=m.mail_id
                    WHERE ( m.Timedate BETWEEN %s AND %s)
                    GROUP BY t.employee_id, m.emailadress_id_id
                    ) m ON ea.emailadress_id=m.emailadress_id_id
                    GROUP BY m.employee_id,ea.employee_id
                    UNION
                    SELECT c.aid, c.aid*0, c.bid FROM 
                        (SELECT a.employee_id as aid, b.employee_id as bid
                        FROM app1_employee a CROSS JOIN app1_employee b
                        EXCEPT (SELECT mid, eid FROM 
                            (SELECT m.employee_id as mid, SUM(m.nbmail), ea.employee_id as eid FROM
                            (SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
                                INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
                            ) ea
                            INNER JOIN
                            (SELECT t.employee_id, COUNT(m.mail_id) AS nbmail, m.emailadress_id_id FROM app1_mail m 
                            RIGHT JOIN
                                (SELECT ea2.employee_id, t.mail_id_id FROM app1_to t 
                                RIGHT JOIN
                                    (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
                                        INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
                                        ON ea2.emailadress_id=t.emailadress_id_id
                                ) t ON t.mail_id_id=m.mail_id
                            WHERE ( m.Timedate BETWEEN %s AND %s)
                            GROUP BY t.employee_id, m.emailadress_id_id
                            ) m ON ea.emailadress_id=m.emailadress_id_id
                            GROUP BY m.employee_id, ea.employee_id ) ea
                        ) ) c )Tdp
                INNER JOIN
                    (SELECT t.employee_id as id_expediteur, SUM(t.nbmail) as nbmail, ea.employee_id as id_destinataire FROM 
                    (SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
                        INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
                    ) ea
                    INNER JOIN
                    (SELECT m.employee_id, COUNT(m.mail_id) AS nbmail, t.emailadress_id_id FROM app1_to t 
                    RIGHT JOIN
                        (SELECT ea2.employee_id, m.mail_id FROM app1_mail m 
                        RIGHT JOIN
                            (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
                                INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
                                ON ea2.emailadress_id=m.emailadress_id_id 
                                WHERE ( m.Timedate BETWEEN %s AND %s)
                        ) m ON t.mail_id_id=m.mail_id
                    GROUP BY m.employee_id, t.emailadress_id_id
                    ) t ON ea.emailadress_id=t.emailadress_id_id
                    GROUP BY t.employee_id,ea.employee_id
                    UNION
                    SELECT c.aid, c.aid*0, c.bid FROM 
                        (SELECT a.employee_id as aid, b.employee_id as bid
                        FROM app1_employee a CROSS JOIN app1_employee b
                        EXCEPT (SELECT mid, eid FROM
                            (SELECT t.employee_id as mid, SUM(t.nbmail) as nbmail, ea.employee_id as eid FROM 
                            (SELECT ea.emailadress_id, emp.employee_id FROM app1_emailadress ea
                                INNER JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id
                            ) ea
                            INNER JOIN
                            (SELECT m.employee_id, COUNT(m.mail_id) AS nbmail, t.emailadress_id_id FROM app1_to t 
                            RIGHT JOIN
                                (SELECT ea2.employee_id, m.mail_id FROM app1_mail m 
                                RIGHT JOIN
                                    (SELECT ea2.emailadress_id, emp2.employee_id FROM app1_emailadress ea2
                                        INNER JOIN app1_employee emp2 ON emp2.employee_id=ea2.employee_id_id) ea2 
                                        ON ea2.emailadress_id=m.emailadress_id_id 
                                        WHERE ( m.Timedate BETWEEN %s AND %s)
                                ) m ON t.mail_id_id=m.mail_id
                            GROUP BY m.employee_id, t.emailadress_id_id
                            ) t ON ea.emailadress_id=t.emailadress_id_id
                            GROUP BY t.employee_id,ea.employee_id ) ea
                        ) ) c )Tdp2
                ON Tdp.id_expediteur=Tdp2.id_destinataire WHERE Tdp.id_destinataire=Tdp2.id_expediteur
                GROUP BY employe1_id, employe2_id, nbgauche_droite, nbdroite_gauche ) T
                INNER JOIN app1_employee empg ON empg.employee_id=T.employe1_id
                INNER JOIN app1_employee empd ON empd.employee_id=T.employe2_id
                WHERE T.nbgauche_droite + T.nbdroite_gauche >= %s
                ORDER BY T.nbgauche_droite+T.nbdroite_gauche DESC 
                """,[datetimea,datetimeb,datetimea,datetimeb,datetimea,datetimeb,datetimea,datetimeb,minm])
                result=cursor.fetchall()
                columns = ["Nom de l'employé(e) 1","Prénom de l'employé(e) 1","Nom l'employé(e) 2","Prénom l'employé(e) 2","Nombre de mails envoyés de 1 à 2","Nombre de mails envoyés de 2 à 1","Total"]   

    if result==[] : 
        return HttpResponse("""<p>Aucun résultat trouvé</p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Formulaire4">Revenir au formulaire de la requête 4</a></p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Accueil">Revenir à la page d'accueil</a></p>
                            """)
    
    tableau=pds.DataFrame(result,columns=columns)
    
    if nomprenom :
        M=np.asarray(tableau)
        AMU=any(M[:,-1]>0) #Au moins un employé a eu un échange.
        if AMU : 
            plt.pie(M[:,-1],labels=M[:,1]+' '+M[:,0],autopct='%1.1f%%')
            plt.title("Diagramme en camembert du nombre de mails par employé")
            plt.savefig('./app1/static/Schema.png')
            plt.clf()
    
    
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau4.html',
        {
            'columns' : tableau.columns,
            'L' : ntableau,
            'C' : Criteres,
            'pie' : nomprenom and AMU,
            'n' : nrow} )
    

