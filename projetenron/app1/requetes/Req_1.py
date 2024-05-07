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

bymail=False
byauthor=True
prenom='Mark'
nom='Taylor'



from app1.models import Employee,Emailadress,Mail,To,Cc #,Re
from django.core.exceptions import ObjectDoesNotExist

from django.db import connection

def req1(request) :
    if byauthor :
        with connection.cursor() as cursor:
            cursor.execute(
            """
            SELECT *
            FROM app1_employee e
            INNER JOIN app1_emailadress ea
                ON e.employee_id=ea.employee_id_id
            WHERE e.lastname=%s AND e.firstname=%s
            """,[nom,prenom])
            result=cursor.fetchall()
            columns = [col[0] for col in cursor.description] 
            
        tableau=pds.DataFrame(result,columns=columns)
        
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[[tableau.index[i]]+list(M[i,:]) for i in range(nrow)]
    return render(request,'tableau.html',
        {
            'index' : tableau.index,
            'columns' : tableau.columns,
            'L' : ntableau,
                  })