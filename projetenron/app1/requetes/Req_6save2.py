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
    
    
    
    
    
    
    reqsql="""
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
        
    """
    reqsql+=" WHERE m.path LIKE '/smith-m/all_documents/%'"
    reqsql+=" GROUP BY m.path, m.emailadress_id_id, m.subject, m.timedate"
    
    
    with connection.cursor() as cursor:
        cursor.execute(reqsql)
        
        result=cursor.fetchall()
        columns = ["Chemin d'accés (cliquez pour ouvrir)","auteur","object","Date et heure d'envoi"]
    
    
    n=len(result)
    mot=["hi","by"]
    
    #Construction de la première colonne
    listelignemot=[set([]) for i in mot]
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
                    if bool(re.search(mot[m],Lignes[k])) : listelignemot[m].add(k+1)
        k+=1
    trouve=False
    for m in range(len(mot)) :
        if len(listelignemot[m])==0 : listelignemot[m]="NA"
        else : trouve=True
        
    DF=pds.DataFrame(dict([(columns[j],[result[0][j]]) for j in range(len(columns))]+[('Tous trouvés',[all(motfind)])]+[('Un seul trouvé',[trouve])]+[(f'Position de la ligne du mot "{mot[m]}"',[listelignemot[m]]) for m in range(len(mot))]), index=[0])
    
    
    for i in range(1,n) :
        listelignemot=[set([]) for i in mot]
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
                        if bool(re.search(mot[m],Lignes[k])) : listelignemot[m].add(k+1)
            k+=1
        trouve=False
        for m in range(len(mot)) :
            if len(listelignemot[m])==0 : listelignemot[m]="NA"
            else : trouve=True
                    
        DF=pds.concat((DF,pds.DataFrame(dict([(columns[j],[result[i][j]]) for j in range(len(columns))]+[('Tous trouvés',[all(motfind)])]+[('Un seul trouvé',[trouve])]+[(f'Position de la ligne du mot "{mot[m]}"',[listelignemot[m]]) for m in range(len(mot))]), index=[i])))    
        print(f"concaténation à {round(100*(i+1)/n,2)}{r'%'}")
    
    tableau=DF[DF['Un seul trouvé']==True]
    tableau.replace(set(),"NA")
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau6.html',
        {
        'index' : tableau.index,
        'columns' : tableau.columns,
        'L' : ntableau,
        'p' : 1
              })
