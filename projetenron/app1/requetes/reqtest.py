from django.shortcuts import render
from django.http import HttpResponse
import pandas as pds
import numpy as np
import os
import os.path as osp



import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '../monprojet.settings') 
django.setup()

from app1.models import Employee,Emailadress,Mail,To,Cc


def extableau2(request) :
    tableau=pds.read_csv("recherchemot.csv",index_col=(0))
    p=list(tableau.columns).index('path')+2 #rang de la colonne "path"
    nrow=tableau.shape[0]
    M=np.asarray(tableau)
    ntableau=[[tableau.index[i]]+list(M[i,:]) for i in range(nrow)]
    return render(request,'extableau2.html',
        {
            'index' : tableau.index,
            'columns' : tableau.columns,
            'L' : ntableau,
            'p' : p
                  })



