#!/bin/env python3

import re
import os
import os.path as osp 
import datetime as dt
import django
import matplotlib.pyplot as plt
import pandas as pds

#'django_extensions' ##Pour éxecuter la commande au projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetenron.settings') 
django.setup()

from app1.models import Employee,Emailadress,Mail,To,Cc #,Re
from django.core.exceptions import ObjectDoesNotExist

from django.db import connection

jour=dt.datetime(2000,1,1)
listejour,liste_internes_externes,liste_internes=[],[],[]
while jour < dt.datetime(2002,1,1) : 
    with connection.cursor() as cursor:
        cursor.execute(
        """
        SELECT COUNT(T.mail_id) FROM (
        SELECT m.mail_id, m.subject, m.emailadress_id_id, t.dest_interne, aut.interne as exp_interne FROM app1_mail m 
            INNER JOIN 
            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
            GROUP BY t.mail_id_id
            ) t ON t.mail_id_id=m.mail_id
            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
            WHERE (m.Timedate - interval '9 hours' BETWEEN %s AND %s) AND ((aut.interne=True AND t.dest_interne=false) OR (aut.interne=False AND t.dest_interne=True)) /*OU exclusive, au soit le destinataire ou soit l'expéditeur est interne mais pas les deux*/
        ) T 
        """,[str(jour),str(jour+dt.timedelta(days=1))]) #Le "- interval '9 hours'" est pour remettre l'heure au fuseau horaire des mails (-0700 (PDT) en heure d'été et -0800 (PST) en heure d'hiver)
        liste_internes_externes.append(cursor.fetchone()[0]) #En effet les timedate dans la base de donnée sont en +0200 en heure d'été et en +0100 en heure d'hiver.
        
    with connection.cursor() as cursor:
        cursor.execute(
        """
        SELECT COUNT(T.mail_id) FROM (
        SELECT m.mail_id, m.subject, m.emailadress_id_id, t.dest_interne, aut.interne as exp_interne FROM app1_mail m 
            INNER JOIN 
            (SELECT t.mail_id_id, bool_and(ea.interne) as dest_interne FROM app1_to t
            INNER JOIN app1_emailadress ea ON ea.emailadress_id=t.emailadress_id_id 
            GROUP BY t.mail_id_id
            ) t ON t.mail_id_id=m.mail_id
            INNER JOIN app1_emailadress aut ON aut.emailadress_id=m.emailadress_id_id
            WHERE (m.Timedate - interval '9 hours' BETWEEN %s AND %s) AND (aut.interne=True AND t.dest_interne=True) 
        ) T
        """,[str(jour),str(jour+dt.timedelta(days=1))])
        liste_internes.append(cursor.fetchone()[0])
    print(f"Calcul du nombre de mails échangés à la date {jour}")
    listejour.append(jour)     
    jour=jour+dt.timedelta(days=1)


print(len(listejour),len(liste_internes_externes),len(liste_internes))

DF=pds.DataFrame({"Jour":listejour,"internes_externes":liste_internes_externes,"internes":liste_internes})
DF["Total"]=DF["internes_externes"]+DF["internes"]
print(DF)

print(DF.sort_values("Total",ascending=False))
#Si on veut afficher 
plt.bar(listejour,liste_internes_externes)
plt.show()












