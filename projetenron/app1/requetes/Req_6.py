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

# mots='hi;by'
# mots=mots.split(';')

# path='/smith-m'

# emailaut=''

# emaildest=''#'matt.smith@enron.com'

# prenomaut=''
# nomaut=''

# prenomdest=''#'Matt'
# nomdest=''#'Smith'

# subject=''
    
# joura='2001-10-29'
# heurea=''
# datetimea=joura+' '+heurea

# jourb='2001-11-27'
# heureb=''
# datetimeb=jourb+' '+heureb

# #"0" non précisé, "1" : interne, "2" : externe
# natautinterne='2'
# natdestinterne='2'

# Tousresultats=False

def req6(request) :
    rP=request.POST
    
    mots=rP["mots"]
    
    Criteres=f"Listes des mots : {mots}"
    
    mots=mots.split(';')

    path=rP["path"]

    emailaut=rP["emailaut"]

    emaildest=rP["emaildest"]

    prenomaut=rP["prenomaut"]
    nomaut=rP["nomaut"]

    prenomdest=rP["prenomdest"]
    nomdest=rP["nomdest"]

    subject=rP["subject"]
        
    joura=rP["joura"]
    heurea=rP["heurea"]
    datetimea=joura+' '+heurea

    jourb=rP["jourb"]
    heureb=rP["heureb"]
    datetimeb=jourb+' '+heureb

    #"0" non précisé, "1" : interne, "2" : externe
    natautinterne=rP["natautinterne"]
    natdestinterne=rP["natdestinterne"]
    
    Criteres+=', Auteurs internes'*(natautinterne=="1")+', Auteurs externes'*(natautinterne=="2")
    Criteres+=', Destinataires internes'*(natdestinterne=="1")+', Destinataires externes'*(natdestinterne=="2")

    Tousresultats="Tousresultats" in rP

    reqsql="""
    SELECT m.path, m.emailadress_id_id as auteur, m.subject, m.timedate FROM app1_mail m
        LEFT JOIN 
        (SELECT ea.emailadress_id, ea.interne, emp.firstname, emp.lastname FROM app1_emailadress ea 
            LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) aut 
        ON aut.emailadress_id=m.emailadress_id_id
        LEFT JOIN 
        (SELECT t.mail_id_id, bool_and(ea2.interne) as interne FROM app1_to t 
            INNER JOIN app1_emailadress ea2 
                ON t.emailadress_id_id=ea2.emailadress_id 
            GROUP BY t.mail_id_id ) dint 
        ON m.mail_id=dint.mail_id_id
        LEFT JOIN
        (SELECT t.mail_id_id, eadest.emailadress_id, eadest.firstname, eadest.lastname FROM app1_to t 
            LEFT JOIN 
            (SELECT ea.emailadress_id, emp.firstname, emp.lastname FROM app1_emailadress ea 
                LEFT JOIN app1_employee emp ON emp.employee_id=ea.employee_id_id) eadest
            ON t.emailadress_id_id=eadest.emailadress_id ) dest 
        ON m.mail_id=dest.mail_id_id
    """
    fwhere=False
    
    if path!='' : 
        Criteres+=f", Chemin d'accés : {path}"
        if fwhere : reqsql+=f" AND m.path LIKE '{path}%'" 
        else : 
            reqsql+=f" WHERE m.path LIKE '{path}%'"
            fwhere=True
    
    if emailaut!='' :
        Criteres+=f", Adresse email de l'auteur : {emailaut}"
        if fwhere : reqsql+=f" AND aut.emailadress_id = '{emailaut}'" 
        else : 
            reqsql+=f" WHERE aut.emailadress_id = '{emailaut}'"
            fwhere=True
    
    if emaildest!='' :
        Criteres+=f", Adresse email du destinataire : {emaildest}"
        if fwhere : reqsql+=f" AND dest.emailadress_id = '{emaildest}'" 
        else : 
            reqsql+=f" WHERE dest.emailadress_id = '{emaildest}'"
            fwhere=True
    
    if prenomaut!='' and nomaut!='' :
        Criteres+=f", Prénom de l'auteur : {prenomaut}, Nom de l'auteur : {nomaut}"
        if fwhere : reqsql+=f" AND aut.firstname='{prenomaut}' AND aut.lastname='{nomaut}'" 
        else : 
            reqsql+=f" WHERE aut.firstname='{prenomaut}' AND aut.lastname='{nomaut}'"
            fwhere=True
    
    if prenomdest!='' and nomdest!='' :
        Criteres+=f", Prénom du destinataire : {prenomdest}, Nom du destinataire: {nomdest}"
        if fwhere : reqsql+=f" AND dest.firstname='{prenomdest}' AND dest.lastname='{nomdest}'" 
        else : 
            reqsql+=f" WHERE dest.firstname='{prenomdest}' AND dest.lastname='{nomdest}'"
            fwhere=True
    
    if subject!='' :
        Criteres+=f", Objet : {subject}"
        if fwhere : reqsql+=f" AND m.subject = '{subject}'" 
        else : 
            reqsql+=f" WHERE m.subject = '{subject}'"
            fwhere=True
    
    if joura!='' :
        Criteres+=f", Après le {datetimea}"
        if fwhere : reqsql+=f" AND m.timedate >= '{datetimea}'" 
        else : 
            reqsql+=f" WHERE m.timedate >= '{datetimea}'"
            fwhere=True
            
    if jourb!='' :
        Criteres+=f", Avant le {datetimeb}"
        if fwhere : reqsql+=f" AND m.timedate <= '{datetimeb}'" 
        else : 
            reqsql+=f" WHERE m.timedate <= '{datetimeb}'"
            fwhere=True 
    
    if natautinterne=="1" : 
        if fwhere : reqsql+=" AND aut.interne = True" 
        else : 
            reqsql+=" WHERE aut.interne = True"
            fwhere=True 
    elif natautinterne=="2" :
        if fwhere : reqsql+=" AND aut.interne = False" 
        else : 
            reqsql+=" WHERE aut.interne = False"
            fwhere=True 
    
    if natdestinterne=="1" : 
        if fwhere : reqsql+=" AND dint.interne = True" 
        else : 
            reqsql+=" WHERE dint.interne = True"
            fwhere=True 
    elif natdestinterne=="2" :
        if fwhere : reqsql+=" AND dint.interne = False" 
        else : 
            reqsql+=" WHERE dint.interne = False"
            fwhere=True 
    
    
    reqsql+=" GROUP BY m.path, m.emailadress_id_id, m.subject, m.timedate"
    
    with connection.cursor() as cursor:
        cursor.execute(reqsql)
        result=cursor.fetchall()
        columns = ["Chemin d'accés (cliquez pour ouvrir)","auteur","objet","Date et heure d'envoi"]
    
    n=len(result)
    
    resultat=False #Est ce qu'on a trouvé un resultat, c'est-à-dire si le dataframe tableau existe
    
    for i in range(0,n) :
        listelignemot=[set([]) for i in mots]
        motfind=[False for i in mots]
        
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
                    for m in range(len(mots)) : 
                        motfind[m]=motfind[m] or bool(re.search(mots[m],Lignes[k]))
                        if bool(re.search(mots[m],Lignes[k])) : listelignemot[m].add(k+1)
            k+=1
        trouve=False
        for m in range(len(mots)) :
            if len(listelignemot[m])==0 : listelignemot[m]="NA"
            else : trouve=True
            
        if trouve :
            if not resultat :
                tableau = pds.DataFrame(dict([(columns[j],[result[i][j]]) for j in range(len(columns))]+[('Tous trouvés',[all(motfind)])]+[(f'Position de la ligne du mot "{mots[m]}"',[listelignemot[m]]) for m in range(len(mots))]), index=[i])
                resultat = True
            else :
                tableau =pds.concat((tableau,pds.DataFrame(dict([(columns[j],[result[i][j]]) for j in range(len(columns))]+[('Tous trouvés',[all(motfind)])]+[(f'Position de la ligne du mot "{mots[m]}"',[listelignemot[m]]) for m in range(len(mots))]), index=[i]))) 
                             
        print(f"concaténation à {round(100*(i+1)/n,2)}{r'%'}")
           
    if not resultat : 
        return HttpResponse("""<p>Aucun résultat trouvé</p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Formulaire6">Revenir au formulaire de la requête 6</a></p>
                            <p><a href="http://127.0.0.1:7000/Application_Projet/Accueil">Revenir à la page d'accueil</a></p>
                            """)
    
    if Tousresultats : 
        tableau=tableau[tableau['Tous trouvés']==True].drop('Tous trouvés', axis=1)
    
    tableau.replace(set(),"NA")    
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau6.html',
        {
        'index' : tableau.index,
        'columns' : tableau.columns,
        'L' : ntableau,
        'p' : 1,
        'C' : Criteres})
