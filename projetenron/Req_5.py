#!/bin/env python3

import re
import os
import os.path as osp 
import datetime as dt
import django
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

#'django_extensions' ##Pour éxecuter la commande au projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetenron.settings') 
django.setup()

from app1.models import Employee,Emailadress,Mail,To,Cc #,Re
from django.core.exceptions import ObjectDoesNotExist

from django.db import connection

jour=dt.datetime(2001,4,1)
listejour,liste_internes_externes,liste_internes=[],[],[]
while jour < dt.datetime(2001,5,1) : 
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
            WHERE (m.Timedate BETWEEN %s AND %s) AND ((aut.interne=True AND t.dest_interne=false) OR (aut.interne=False AND t.dest_interne=True)) /*OU exclusive, au soit le destinataire ou soit l'expéditeur est interne mais pas les deux*/
        ) T
        """,[str(jour),str(jour+dt.timedelta(days=1))])
        liste_internes_externes.append(cursor.fetchone()[0])
        
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
            WHERE (m.Timedate BETWEEN %s AND %s) AND (aut.interne=True AND t.dest_interne=True) 
        ) T
        """,[str(jour),str(jour+dt.timedelta(days=1))])
        liste_internes.append(cursor.fetchone()[0])
        
    listejour.append(jour)     
    jour=jour+dt.timedelta(days=1)

#print(nb_internes_externes[0],nb_internes[0])


# t1=dt.timedelta(hours=23)
# t2=dt.timedelta(hours=2)
# t3=t1+t2

# t0=dt.datetime(2001, 2, 2)
# print(t0)
# print(t0+t3)

# str(t0)

print(len(listejour),len(liste_internes_externes),len(liste_internes))

plt.plot(listejour,liste_internes_externes)
plt.show()












