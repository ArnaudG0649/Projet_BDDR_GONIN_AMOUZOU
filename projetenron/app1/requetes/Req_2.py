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

interne=False
externe=False
envoyes=True
recus=False
joura='2000-01-01'
heurea='00:00'
jourb='2100-01-01'
heureb='00:00'
minm=1000
def req2(request) :
    
    datetimea=joura+' '+heurea
    datetimeb=jourb+' '+heureb
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
            WHERE nbmail> %s
            ORDER BY nbmail DESC
        """,[datetimea,datetimeb,minm])
        result=cursor.fetchall()
        columns = ['nom','prénom','nombre de mails envoyés'] 
    
    tableau=pds.DataFrame(result,columns=columns)
                
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau.html',
        {
            'columns' : tableau.columns,
            'L' : ntableau,
                  })
    

