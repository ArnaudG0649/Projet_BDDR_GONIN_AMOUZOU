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

#'django_extensions' ##Pour éxecuter la commande au projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetenron.settings') 
django.setup()

from app1.models import Employee,Emailadress,Mail,To,Cc #,Re
from django.core.exceptions import ObjectDoesNotExist

from django.db import connection

def req6(request) :
    with connection.cursor() as cursor:
        cursor.execute(
        """
        SELECT m.path, m.emailadress_id_id as auteur, m.subject, m.timedate FROM app1_mail m
            LEFT JOIN 
            (SELECT ea.emailadress_id, ea.interne, emp.firstname, emp.lastname FROM app1_emailadress ea /*Cette sous-requête récupère tout ce qui concerne les auteurs*/
                LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) aut 
            ON aut.emailadress_id=m.emailadress_id_id
            LEFT JOIN 
            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne FROM app1_to t /*Cette sous-requête permet de dire si un mail a été envoyé qu'à des destinataires internes ou s'il y a un destinataires externes dans le mail*/
                INNER JOIN app1_emailadress ea2 
                    ON t.emailadress_id_id=ea2.emailadress_id 
                GROUP BY t.mail_id_id ) dint 
            ON m.mail_id=dint.mail_id_id
            LEFT JOIN
            (SELECT t.mail_id_id, t.emailadress_id_id, eadest.firstname, eadest.lastname FROM app1_to t /*Cette sous-requête récupère tout ce qui concerne les destinataires*/
                LEFT JOIN 
                (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_emailadress ea 
                    LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) eadest
                ON t.emailadress_id_id=eadest.emailadress_id ) dest 
            ON m.mail_id=dest.mail_id_id
            WHERE m.path LIKE '/dickson-s%'
            /* WHERE m.Timedate > '2001-01-01' AND dest.firstname='Jeff' AND dest.lastname='King' AND aut.interne=True /*Ensuite on filtre ce qu'on veut*/ */
        GROUP BY m.path, m.emailadress_id_id, m.subject, m.timedate 
        """)
        result=cursor.fetchall()
        columns = [col[0] for col in cursor.description]
    
    
    n=len(result)
    mot=["hi","by"]
    
    #Construction de la première colonne
    listelignemot=set(())
    motfind=[False for i in mot]
    
    try : 
        with open(osp.join(os.getcwd(),osp.join('maildir',result[0][0][1:])),"r") as file :
            Lignes=[ligne for ligne in file]
    except UnicodeDecodeError :
        with open(osp.join(os.getcwd(),osp.join('maildir',result[0][0][1:])),"rb") as file :
            Lignes=str(file.read()).split(r'\n')
    nblignes=len(Lignes)    
    entexte=False
    fini=False
    k=0
    while k in range(nblignes) and not fini :
        if not entexte : 
            if Lignes[k]=='\n' : entexte=True
        else :        
            if re.search(r"---------------------- Forwarded",Lignes[k]) or re.search(r"-----Original Message-----",Lignes[k]) : 
                fini=True
            else : 
                for m in range(len(mot)) : 
                    motfind[m]=motfind[m] or bool(re.search(mot[m],Lignes[k]))
                    if bool(re.search(mot[m],Lignes[k])) : listelignemot.add(k+1)
        k+=1
    
    
    DF=pds.DataFrame(dict([(columns[j],[result[0][j]]) for j in range(len(columns))]+[('AllFind',[all(motfind)])]+[('OneFind',[len(listelignemot)>0])]+[('Line',[listelignemot])]), index=[0])
    
    
    for i in range(1,n) :
        listelignemot=set(())
        motfind=[False for i in mot]
        
        try : 
            with open(osp.join(os.getcwd(),osp.join('maildir',result[i][0][1:])),"r") as file :
                Lignes=[ligne for ligne in file]
        except UnicodeDecodeError :
            with open(osp.join(os.getcwd(),osp.join('maildir',result[i][0][1:])),"rb") as file :
                Lignes=str(file.read()).split(r'\n')
        nblignes=len(Lignes)    
        entexte=False
        fini=False
        k=0
        while k in range(nblignes) and not fini :
            if not entexte : 
                if Lignes[k]=='\n' : entexte=True
            else :        
                if re.search(r"---------------------- Forwarded",Lignes[k]) or re.search(r"-----Original Message-----",Lignes[k]) : 
                    fini=True
                else : 
                    for m in range(len(mot)) : 
                        motfind[m]=motfind[m] or bool(re.search(mot[m],Lignes[k]))
                        if bool(re.search(mot[m],Lignes[k])) : listelignemot.add(k+1)
            k+=1
            
        DF=pds.concat((DF,pds.DataFrame(dict([(columns[j],[result[i][j]]) for j in range(len(columns))]+[('AllFind',[all(motfind)])]+[('OneFind',[len(listelignemot)>0])]+[('Line',[listelignemot])]), index=[i])))    
        print(f"concaténation à {round(100*(i+1)/n,2)}{r'%'}")
    
    tableau=DF[DF['OneFind']==True]
    p=list(tableau.columns).index('path')+1 #rang de la colonne "path"
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau6.html',
        {
        'index' : tableau.index,
        'columns' : tableau.columns,
        'L' : ntableau,
        'p' : p
              })


# for i in range(1,n) : 
#     DF=pds.concat((DF,pds.DataFrame(dict([(columns[j],[result[i][j]]) for j in range(len(columns))]), index=[i])))
#     print(f"concaténation à {round(100*(i+1)/n,2)}{r'%'}")
    
# DF['OneFind']=[False for i in range(n)]
# DF['AllFind']=[False for i in range(n)]
# DF['Line']=[set(()) for i in range(n)]



# listelignemot=set(()) #=DF['Line'][i]
# mot=["have","I","feel"]
# motfind=[False for i in mot]

# try : 
#     with open("/users/2024/ds1/122005148/Bureau/projet_BDDR/ex_reponses/288.","r") as file :
#         Lignes=[ligne for ligne in file]
# except UnicodeDecodeError :
#     with open("/users/2024/ds1/122005148/Bureau/projet_BDDR/ex_reponses/288.","rb") as file :
#         Lignes=str(file.read()).split(r'\n')
# nblignes=len(Lignes)

# entexte=False
# fini=False
# k=0
# while k in range(nblignes) and not fini :
#     if not entexte : 
#         if Lignes[k]=='\n' : entexte=True
#     else :        
#         if re.search(r"---------------------- Forwarded",Lignes[k]) or re.search(r"-----Original Message-----",Lignes[k]) : 
#             fini=True
#         else : 
#             for m in range(len(mot)) : 
#                 motfind[m]=motfind[m] or bool(re.search(mot[m],Lignes[k]))
#                 if bool(re.search(mot[m],Lignes[k])) : listelignemot.add(k+1)
#     print(k+1,listelignemot)
#     k+=1
# totfind=all(motfind) #=DF['AllFind'][i]
# #DF['OneFind']=len(listelignemot>0)
# print(totfind)

# Lignes[15]
#carson-m/all_documents/149. ex fw
#'/carson-m/all_documents/149.'[1:]
#"mims-thurston-p/all_documents/9."
#osp.join(os.getcwd(),osp.join('maildir','carson-m/all_documents/149.'))