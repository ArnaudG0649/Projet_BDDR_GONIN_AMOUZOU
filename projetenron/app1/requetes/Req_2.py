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


# interne=True
# externe=True
# envoyes=True
# recus=True


# joura='2001-01-01'
# heurea='00:00'
# jourb='2100-01-01'
# heureb='00:00'
# minm=1000

def req2(request) :
    rP=request.POST
    interne="interne" in rP
    externe="externe" in rP
    envoyes="envoyes" in rP
    recus="recus" in rP
    LD=[interne,externe,envoyes,recus]
    joura=rP["joura"]
    heurea=rP["heurea"]
    jourb=rP["jourb"]
    heureb=rP["heureb"]
    minm=rP["minm"]
    
    
    datetimea=joura+' '+heurea
    datetimeb=jourb+' '+heureb
    
    
    if LD==[False,False,False,False] : 
        return HttpResponse("<p>Cochez au moins une case !</p>")
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails envoyés
    elif LD==[False,False,True,False] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT lastname,firstname,nbmail FROM
                (SELECT emp.lastname,emp.firstname, COUNT(*) as nbmail   
                    FROM app1_emailadress ea
                    INNER JOIN app1_employee emp
                        ON emp.employee_id=ea.employee_id_id
                    INNER JOIN app1_mail m 
                        ON m.emailadress_id_id=ea.emailadress_id
                    WHERE Timedate BETWEEN %s AND %s
                    GROUP BY emp.employee_id
                ) T
                WHERE nbmail >= %s
                ORDER BY nbmail DESC
            """,[datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails envoyés'] 
    
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails reçus
    elif LD==[False,False,False,True] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT lastname,firstname,nbmail FROM
                (SELECT emp.lastname,emp.firstname, COUNT(*) as nbmail   
                    FROM app1_emailadress ea
                    INNER JOIN app1_employee emp
                        ON emp.employee_id=ea.employee_id_id
                    INNER JOIN app1_to t
                        ON t.emailadress_id_id=ea.emailadress_id
                    INNER JOIN app1_mail m 
                        ON m.mail_id=t.mail_id_id
                    WHERE Timedate BETWEEN %s AND %s
                    GROUP BY emp.employee_id
                ) T
                WHERE nbmail >= %s
                ORDER BY nbmail DESC
            """,[datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails reçus'] 
    
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails envoyés et reçus
    elif LD==[False,False,True,True] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT Env.lastname, Env.firstname, Env.nbenv, Rec.nbrec, Rec.nbrec+Env.nbenv AS total FROM
                (SELECT emp.employee_id, emp.lastname,emp.firstname, COUNT(m.mail_id) as nbenv   
                    FROM app1_employee emp
                    INNER JOIN app1_emailadress ea 
                        ON emp.employee_id=ea.employee_id_id
                    LEFT JOIN (SELECT emailadress_id_id, mail_id FROM app1_mail WHERE Timedate BETWEEN %s AND %s ) m
                        ON m.emailadress_id_id=ea.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname,emp.firstname
                ) Env
            INNER JOIN 
                (SELECT emp.employee_id, emp.lastname,emp.firstname, COUNT(t.mail_id_id) as nbrec  
                    FROM app1_employee emp
                    INNER JOIN app1_emailadress ea 
                        ON emp.employee_id=ea.employee_id_id
                    LEFT JOIN 
                    (SELECT t.mail_id_id, t.emailadress_id_id FROM app1_to t
                        LEFT JOIN app1_mail m ON t.mail_id_id=m.mail_id
                        WHERE Timedate BETWEEN %s AND %s
                     ) t
                        ON t.emailadress_id_id=ea.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname,emp.firstname
                ) Rec
                ON Env.employee_id=Rec.employee_id
                WHERE Rec.nbrec+Env.nbenv >= %s
                ORDER BY Rec.nbrec+Env.nbenv DESC
            """,[datetimea,datetimeb,datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails envoyés','nombre de mails reçus','total']
            
    #LD=[interne,externe,envoyes,recus] #nombre de mails internes avec détails
    elif LD==[True,False,True,True] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT Env.lastname, Env.firstname, Env.nbenv, Rec.nbrec, Rec.nbrec+Env.nbenv as total FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m 
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = True AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname
                    ) Env
                INNER JOIN
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
                    FROM 
                        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                        ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne 
                        FROM app1_to t
                        INNER JOIN app1_mail m
                            ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2
                            ON ea2.emailadress_id=m.emailadress_id_id
                        WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=True
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) Rec
                ON Env.employee_id=Rec.employee_id
                WHERE Rec.nbrec+Env.nbenv >= %s
                ORDER BY Rec.nbrec+Env.nbenv DESC
            """,[datetimea,datetimeb,datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails internes envoyés','nombre de mails internes reçus','total']
    
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails internes sans détail
    elif LD==[True,False,False,False] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT Env.lastname, Env.firstname, Rec.nbrec+Env.nbenv as total FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m 
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = True AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname
                    ) Env
                INNER JOIN
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
                    FROM 
                        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                        ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne 
                        FROM app1_to t
                        INNER JOIN app1_mail m
                            ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2
                            ON ea2.emailadress_id=m.emailadress_id_id
                        WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=True
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) Rec
                ON Env.employee_id=Rec.employee_id
                WHERE Rec.nbrec+Env.nbenv >= %s
                ORDER BY Rec.nbrec+Env.nbenv DESC
            """,[datetimea,datetimeb,datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails internes échangés']
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails externes avec détails
    elif LD==[False,True,True,True] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT Env.lastname, Env.firstname, Env.nbenv, Rec.nbrec, Rec.nbrec+Env.nbenv as total FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m 
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = False AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname
                    ) Env
                INNER JOIN
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
                    FROM 
                        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                        ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne 
                        FROM app1_to t
                        INNER JOIN app1_mail m
                            ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2
                            ON ea2.emailadress_id=m.emailadress_id_id
                        WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=False
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) Rec
                ON Env.employee_id=Rec.employee_id
                WHERE Rec.nbrec+Env.nbenv >= %s
                ORDER BY Rec.nbrec+Env.nbenv DESC
            """,[datetimea,datetimeb,datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails externes envoyés','nombre de mails externes reçus','total']
    
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails externes sans détail
    elif LD==[False,True,False,False] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT Env.lastname, Env.firstname, Rec.nbrec+Env.nbenv as total FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m 
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = False AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname
                    ) Env
                INNER JOIN
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
                    FROM 
                        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                        ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne 
                        FROM app1_to t
                        INNER JOIN app1_mail m
                            ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2
                            ON ea2.emailadress_id=m.emailadress_id_id
                        WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=False
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) Rec
                ON Env.employee_id=Rec.employee_id
                WHERE Rec.nbrec+Env.nbenv >= %s
                ORDER BY Rec.nbrec+Env.nbenv DESC
            """,[datetimea,datetimeb,datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails externes échangés']
    

    #LD=[interne,externe,envoyes,recus] #nombre de mails envoyés avec détails
    elif LD==[True,True,True,False] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT Ti.lastname, Ti.firstname, Ti.nbinterne, Te.nbexterne, (Ti.nbinterne + Te.nbexterne) as nbmail FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbinterne  FROM 
                    (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                    ) emp
                    LEFT JOIN 
                    (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                        (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                FROM app1_to t 
                                INNER JOIN app1_emailadress ea2 
                                    ON t.emailadress_id_id=ea2.emailadress_id 
                            GROUP BY t.mail_id_id
                            ) t0
                        INNER JOIN app1_mail m 
                            ON m.mail_id=t0.mail_id_id
                        WHERE  t0.interne = True AND m.Timedate BETWEEN %s AND %s
                    ) m
                        ON m.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id,emp.lastname,emp.firstname
                )Ti
                INNER JOIN 
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbexterne FROM 
                    (SELECT emp.lastname,emp.firstname, ea.emailadress_id,emp.employee_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                    ) emp
                    LEFT JOIN 
                    (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                        (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                FROM app1_to t 
                                INNER JOIN app1_emailadress ea2 
                                    ON t.emailadress_id_id=ea2.emailadress_id 
                            GROUP BY t.mail_id_id
                            ) t0
                        INNER JOIN app1_mail m 
                            ON m.mail_id=t0.mail_id_id
                        WHERE  t0.interne = False AND m.Timedate BETWEEN %s AND %s
                    ) m
                        ON m.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id,emp.lastname,emp.firstname
                )Te
                ON Ti.employee_id=Te.employee_id
                WHERE Ti.nbinterne + Te.nbexterne >= %s
                ORDER BY Ti.nbinterne + Te.nbexterne DESC
            """,[datetimea,datetimeb,datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails internes envoyés','nombre de mails externes envoyés','total']
            
            
    #LD=[interne,externe,envoyes,recus] #nombre de mails reçus avec détails
    elif LD==[True,True,False,True] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT Ti.lastname, Ti.firstname, Ti.nbinterne, Te.nbexterne, (Ti.nbinterne + Te.nbexterne) as nbmail FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbinterne 
                FROM 
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                    FROM app1_emailadress ea
                    INNER JOIN app1_employee emp
                        ON emp.employee_id=ea.employee_id_id
                    ) emp
                LEFT JOIN 
                    (SELECT t.emailadress_id_id, m.mail_id, ea2.interne
                    FROM app1_to t
                    INNER JOIN app1_mail m
                        ON m.mail_id = t.mail_id_id
                    INNER JOIN app1_emailadress ea2
                        ON ea2.emailadress_id=m.emailadress_id_id
                    WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=True
                    ) t
                    ON t.emailadress_id_id=emp.emailadress_id
                GROUP BY emp.employee_id, emp.lastname, emp.firstname
                ) Ti
                INNER JOIN 
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbexterne 
                FROM 
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id
                    FROM app1_emailadress ea
                    INNER JOIN app1_employee emp
                        ON emp.employee_id=ea.employee_id_id
                    ) emp
                LEFT JOIN 
                    (SELECT t.emailadress_id_id, m.mail_id, ea2.interne
                    FROM app1_to t
                    INNER JOIN app1_mail m
                        ON m.mail_id = t.mail_id_id
                    INNER JOIN app1_emailadress ea2
                        ON ea2.emailadress_id=m.emailadress_id_id
                    WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=False
                    ) t
                    ON t.emailadress_id_id=emp.emailadress_id
                GROUP BY emp.employee_id, emp.lastname, emp.firstname
                ) Te
                ON Ti.employee_id=Te.employee_id
                WHERE Ti.nbinterne + Te.nbexterne >= %s
                ORDER BY Ti.nbinterne + Te.nbexterne DESC
                """,[datetimea,datetimeb,datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails internes reçus','nombre de mails externes reçus','total']
    
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails internes envoyés
    elif LD==[True,False,True,False] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT T.lastname, T.firstname, T.nb FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nb FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m 
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = True AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname) T
                WHERE nb >= %s
                ORDER BY nb DESC
            """,[datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails internes envoyés']
    
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails externes envoyés
    elif LD==[False,True,True,False] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT T.lastname, T.firstname, T.nb FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nb FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m 
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = False AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname) T
                WHERE nb >= %s
                ORDER BY nb DESC
            """,[datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails externes envoyés']
    
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails internes reçus
    elif LD==[True,False,False,True] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT Ti.lastname, Ti.firstname, Ti.nb FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nb 
                FROM 
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                    FROM app1_emailadress ea
                    INNER JOIN app1_employee emp
                        ON emp.employee_id=ea.employee_id_id
                    ) emp
                LEFT JOIN 
                    (SELECT t.emailadress_id_id, m.mail_id, ea2.interne 
                    FROM app1_to t
                    INNER JOIN app1_mail m
                        ON m.mail_id = t.mail_id_id
                    INNER JOIN app1_emailadress ea2
                        ON ea2.emailadress_id=m.emailadress_id_id
                    WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=True
                    ) t
                    ON t.emailadress_id_id=emp.emailadress_id
                GROUP BY emp.employee_id, emp.lastname, emp.firstname
                ) Ti
                WHERE Ti.nb >= %s
                ORDER BY nb DESC
            """,[datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails internes reçus']
    
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails externes reçus
    elif LD==[False,True,False,True] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT Ti.lastname, Ti.firstname, Ti.nb FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nb 
                FROM 
                    (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                    FROM app1_emailadress ea
                    INNER JOIN app1_employee emp
                        ON emp.employee_id=ea.employee_id_id
                    ) emp
                LEFT JOIN 
                    (SELECT t.emailadress_id_id, m.mail_id, ea2.interne 
                    FROM app1_to t
                    INNER JOIN app1_mail m
                        ON m.mail_id = t.mail_id_id
                    INNER JOIN app1_emailadress ea2
                        ON ea2.emailadress_id=m.emailadress_id_id
                    WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=False
                    ) t
                    ON t.emailadress_id_id=emp.emailadress_id
                GROUP BY emp.employee_id, emp.lastname, emp.firstname
                ) Ti
                WHERE Ti.nb >= %s
                ORDER BY nb DESC
            """,[datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails externes reçus']    
    
    #LD=[interne,externe,envoyes,recus] #nombre de mails internes et externes échangés 
    elif LD==[True,True,False,False] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
        SELECT INTE.lastname, INTE.firstname, INTE.nbenvint + INTE.nbrecint as nbint, EXT.nbenvext + EXT.nbrecext as nbext, INTE.nbenvint + INTE.nbrecint + EXT.nbenvext + EXT.nbrecext as total FROM
            (SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv as nbenvint, Rec.nbrec as nbrecint FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = True AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname
                    ) Env
                INNER JOIN
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
                    FROM 
                        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                        ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne
                        FROM app1_to t
                        INNER JOIN app1_mail m
                            ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2
                            ON ea2.emailadress_id=m.emailadress_id_id
                        WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=True
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) Rec
                ON Env.employee_id=Rec.employee_id ) INTE
            INNER JOIN 
            (SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv as nbenvext, Rec.nbrec as nbrecext FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m 
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = False AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname
                    ) Env
                INNER JOIN
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
                    FROM 
                        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                        ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne 
                        FROM app1_to t
                        INNER JOIN app1_mail m
                            ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2
                            ON ea2.emailadress_id=m.emailadress_id_id
                        WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=False
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) Rec
                ON Env.employee_id=Rec.employee_id) EXT
            ON INTE.employee_id=EXT.employee_id
            WHERE INTE.nbenvint + INTE.nbrecint + EXT.nbenvext + EXT.nbrecext >= %s
            ORDER BY total DESC
            """,[datetimea,datetimeb,datetimea,datetimeb,datetimea,datetimeb,datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails internes échangés','nombre de mails externes échangés','total']   
    
    
    #LD=[interne,externe,envoyes,recus] #TOUT 
    elif LD==[True,True,True,True] : 
        with connection.cursor() as cursor:
            cursor.execute(
            """
        SELECT INTE.lastname, INTE.firstname, INTE.nbenvint, INTE.nbrecint, EXT.nbenvext, EXT.nbrecext, INTE.nbenvint + INTE.nbrecint + EXT.nbenvext + EXT.nbrecext as total FROM
            (SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv as nbenvint, Rec.nbrec as nbrecint FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = True AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname
                    ) Env
                INNER JOIN
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
                    FROM 
                        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                        ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne
                        FROM app1_to t
                        INNER JOIN app1_mail m
                            ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2
                            ON ea2.emailadress_id=m.emailadress_id_id
                        WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=True
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) Rec
                ON Env.employee_id=Rec.employee_id ) INTE
            INNER JOIN 
            (SELECT Env.employee_id, Env.lastname, Env.firstname, Env.nbenv as nbenvext, Rec.nbrec as nbrecext FROM
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(m.mail_id) as nbenv  FROM 
                        (SELECT emp.lastname,emp.firstname, ea.emailadress_id, emp.employee_id 
                            FROM app1_emailadress ea
                            INNER JOIN app1_employee emp
                                ON emp.employee_id=ea.employee_id_id
                        ) emp
                        LEFT JOIN 
                        (SELECT m.emailadress_id_id, m.mail_id, t0.interne FROM 
                            (SELECT t.mail_id_id, bool_and(ea2.interne) as interne 
                                    FROM app1_to t 
                                    INNER JOIN app1_emailadress ea2 
                                        ON t.emailadress_id_id=ea2.emailadress_id 
                                GROUP BY t.mail_id_id
                                ) t0
                            INNER JOIN app1_mail m 
                                ON m.mail_id=t0.mail_id_id
                            WHERE  t0.interne = False AND m.Timedate BETWEEN %s AND %s
                        ) m
                            ON m.emailadress_id_id=emp.emailadress_id
                        GROUP BY emp.employee_id,emp.lastname,emp.firstname
                    ) Env
                INNER JOIN
                (SELECT emp.employee_id, emp.lastname, emp.firstname, COUNT(t.mail_id) as nbrec 
                    FROM 
                        (SELECT emp.employee_id, emp.lastname, emp.firstname, ea.emailadress_id 
                        FROM app1_emailadress ea
                        INNER JOIN app1_employee emp
                            ON emp.employee_id=ea.employee_id_id
                        ) emp
                    LEFT JOIN 
                        (SELECT t.emailadress_id_id, m.mail_id, ea2.interne 
                        FROM app1_to t
                        INNER JOIN app1_mail m
                            ON m.mail_id = t.mail_id_id
                        INNER JOIN app1_emailadress ea2
                            ON ea2.emailadress_id=m.emailadress_id_id
                        WHERE m.Timedate BETWEEN %s AND %s AND ea2.interne=False
                        ) t
                        ON t.emailadress_id_id=emp.emailadress_id
                    GROUP BY emp.employee_id, emp.lastname, emp.firstname
                    ) Rec
                ON Env.employee_id=Rec.employee_id) EXT
            ON INTE.employee_id=EXT.employee_id
            WHERE INTE.nbenvint + INTE.nbrecint + EXT.nbenvext + EXT.nbrecext >= %s
            ORDER BY total DESC
            """,[datetimea,datetimeb,datetimea,datetimeb,datetimea,datetimeb,datetimea,datetimeb,minm])
            result=cursor.fetchall()
            columns = ['nom','prénom','nombre de mails internes envoyés','nombre de mails internes reçus','nombre de mails externes envoyés','nombre de mails externes reçus','total']    
    
    
    
    
    
    tableau=pds.DataFrame(result,columns=columns)
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau.html',
        {
            'columns' : tableau.columns,
            'L' : ntableau,
                  })
    

