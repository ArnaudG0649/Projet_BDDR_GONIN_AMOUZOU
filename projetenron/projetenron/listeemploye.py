#!/bin/env python3

import os
import django

#'django_extensions' ##Pour éxecuter la commande au projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monprojet.settings') 
django.setup()

from app1.models import Employee, Emailadress
from django.core.exceptions import ObjectDoesNotExist

import xml.etree.ElementTree as ET

# with open("employes_enron.xml", encoding="utf-8") as f:
#     for l in f:
        
tree = ET.parse('employes_enron.xml')
root = tree.getroot() #=employees

root.tag #Nom de l'élément

root.attrib
Listeemployees=[]
for employee in root:
    Tliste=[]
    Tliste.append(employee)
    print(employee.tag, employee.attrib)
    for element in employee:
        Tliste.append(element)
        print(r'   |',element.tag, element.attrib)
    Listeemployees.append(Tliste)
    
    

for E in Listeemployees :
    print (E[0].tag,E[0].attrib)
    for e in E[0:] : 
        print("   |",e.tag,e.text,e.attrib)
        
        
      
Table_employees_mails=[]        
for i in range(len(Listeemployees)):
    L=Listeemployees[i]
    Lemail=[e.attrib["address"] for e in L[3:-1]]
    if len(L[0].attrib)>0 : 
        Enregistrement=[i,L[1].text,L[2].text,L[0].attrib['category'],L[-1].text,Lemail]
        # try:
        #     e=Employee.objects.get(employee_id, lastname, firstname, category)
        
        
        
    else : 
        Enregistrement=[i,L[1].text,L[2].text,None,L[-1].text,Lemail]
    Table_employees_mails.append(Enregistrement)
    
print(Table_employees_mails)
#Voilà on a une pseudo table.

