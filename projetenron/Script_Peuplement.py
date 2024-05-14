#!/bin/env python3

import re
import os
import os.path as osp 
import datetime
import django
import xml.etree.ElementTree as ET

#'django_extensions' ##Pour éxecuter la commande au projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetenron.settings') 
django.setup()

from app1.models import Employee,Emailadress,Mail,To,Cc #,Re
from django.core.exceptions import ObjectDoesNotExist


############ Peuplement à partir du fichier xml ############

if __name__=='__main__' :
      
    tree = ET.parse('employes_enron.xml')
    root = tree.getroot() #=employees
    
    root.tag #Nom de l'élément
    
    root.attrib
    Listeemployees=[]
    for employee in root:
        L=[]
        L.append(employee)
        for element in employee:
            L.append(element)
        Listeemployees.append(L)
#On crée un tableau d'éléments de classe etree.ElementTree.Element, ou chaque ligne (L) correspond à un employé.
               
    for i in range(len(Listeemployees)): #Chaque i correspond à un employé
        L=Listeemployees[i]
        Lemail=[e.attrib["address"] for e in L[3:-1]]
        
        if len(L[0].attrib)>0 : 
            try:
                e=Employee.objects.get(employee_id=i+1, lastname=L[1].text, firstname=L[2].text, category=L[0].attrib['category'], mailbox=L[-1].text)
            except ObjectDoesNotExist:
                e=Employee(employee_id=i+1, lastname=L[1].text, firstname=L[2].text, category=L[0].attrib['category'], mailbox=L[-1].text)
                e.save()
                print(f"L'employé.e {L[2].text} {L[1].text} a été rajouté.e à la base de données.")
        else : 
            try:
                e=Employee.objects.get(employee_id=i+1, lastname=L[1].text, firstname=L[2].text, category=None, mailbox=L[-1].text)
            except ObjectDoesNotExist:
                e=Employee(employee_id=i+1, lastname=L[1].text, firstname=L[2].text, category=None, mailbox=L[-1].text)
                e.save()
                print(f"L'employé.e {L[2].text} {L[1].text} a été rajouté.e à la base de données.")
                
        for email_a in Lemail : 
            try : 
                ea=Emailadress.objects.get(employee_id=e, emailadress_id=email_a, interne=True)
            except ObjectDoesNotExist:  
                ea=Emailadress(employee_id=e, emailadress_id=email_a, interne=True)
                ea.save()

            
############ Peuplement à partir des mails ############

class Mailobj() : #On crée une classe de mails. Les attributs des tables seront les attributs des instances de cette classe.
#L'objectif de cette classe est de pouvoir extraire les informations importantes de chaque mail qui seront mises dans les tables.    

    def __init__(self,path) : 
        self.path=path[len(osp.join(os.getcwd(),"maildir/"))-1:] #Chemin qui commence après le "maildir/"
         
        try : 
            with open(path,"r") as file :
                Lignes=[ligne for ligne in file]
        except UnicodeDecodeError :
            with open(path,"rb") as file :
                Lignes=str(file.read()).split(r'\n')
        
        self.id=re.search(r"<(.*)>",Lignes[0]).group(1)
        
        Lmois=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

        d=Lignes[1].split(" ")[1:]
        nummois=Lmois.index(d[2])+1
        delta=datetime.timedelta(hours=-int(d[-2][2]))
        zone=datetime.timezone(delta)
        self.date=datetime.datetime(int(d[3]), nummois, int(d[1]), hour=int(d[4][:2]), minute=int(d[4][3:5]), second=int(d[4][6:]), tzinfo=zone)+datetime.timedelta(hours=-9)
        #On enlève 9h pour avoir les mêmes heures dans la base de données et les fichiers de mails.
        
        if re.search(r"From: (\S*@\S*)",Lignes[2]) : 
            self.fromm=re.search(r"From: (\S*@\S*)",Lignes[2]).group(1) 
        elif re.search(r"From: (.*>)",Lignes[2]) : 
            self.fromm=re.search(r"From: (.*>)",Lignes[2]).group(1) 
        
        i=3
        if re.search(r"To: ([^(\n)]*)",Lignes[i]): 
            s=re.search(r"To: ([^(\n)]*)",Lignes[i]).group(1)
            s=re.sub(r"\s",r"",s) #Pour enlever tous les séparateurs blancs et garder uniquement les virgules comme séparateurs entre les adresses.
            i+=1
            while bool(re.match(r'\t',Lignes[i])) :
                s+=re.sub(r"\s",r"",Lignes[i])
                i+=1
            self.to=s.split(',')
        else : 
            self.to=None
        
        if re.match(r"Subject: ([^(\n)]*)",Lignes[i]): 
            self.subject=re.match(r"Subject: ([^(\n)]*)",Lignes[i]).group(1) 
            i+=1
            if self.subject=="" : self.subject=None
        else : self.subject=None
        
        if re.search(r"Cc: ([^(\n)]*)",Lignes[i]): 
            s=re.search(r"Cc: ([^(\n)]*)",Lignes[i]).group(1)
            s=re.sub(r"\s",r"",s)
            i+=1
            while bool(re.match(r'\t',Lignes[i])) :
                s+=re.sub(r"\s",r"",Lignes[i])
                i+=1
            self.cc=s.split(',')
        else : 
            self.cc=None
        

def ListemailSQL(path=osp.join(os.getcwd(),"maildir"),i=[0]):
    print(path)
    for file in os.listdir(path) : 
        if osp.isfile(osp.join(path,file)) : #C'est ci_dessous que l'on collecte les données du mail
            mail=Mailobj(osp.join(path,file))
            newmail=False
            i[0]+=1
            print(f"{osp.join(os.getcwd(),'maildir',mail.path)}")
            
            try :  #Adresse email de l'expéditeur
                ea=Emailadress.objects.get(emailadress_id=mail.fromm, interne=mail.fromm.endswith(('enron.com','enron.com>')))
            except ObjectDoesNotExist:  
                ea=Emailadress(employee_id=None, emailadress_id=mail.fromm, interne=mail.fromm.endswith(('enron.com','enron.com>')))
                ea.save()
            
            try :  #Table "mail"
                m=Mail.objects.get(mail_id=mail.id,emailadress_id=ea,subject=mail.subject,timedate=mail.date,path=mail.path)
            except ObjectDoesNotExist:
                newmail=True
                m=Mail(mail_id=mail.id,emailadress_id=ea,subject=mail.subject,timedate=mail.date,path=mail.path)
                m.save()
                
                print(f"({i}) Base de données alimentée avec {osp.join(os.getcwd(),'maildir',mail.path)}")
            
            if newmail : #Si le mail est nouveau
            
                if mail.to : 
                    for to in mail.to : #D'abord on regarde si l'adresse de chaque destinataire est déjà enregistrée et on le fait si ce n'est pas la cas
                            try :  
                                to=Emailadress.objects.get(emailadress_id=to, interne=to.endswith(('enron.com','enron.com>')))
                            except ObjectDoesNotExist:  
                                to=Emailadress(employee_id=None, emailadress_id=to, interne=to.endswith(('enron.com','enron.com>')))
                                to.save()
                            
                            #Puis on la rajoute dans la table croisée "To"
                            t=To(emailadress_id=to,mail_id=m)
                            t.save()
                            
                if mail.cc :    
                    for cc in mail.cc :
                            try : 
                                cc=Emailadress.objects.get(emailadress_id=cc, interne=cc.endswith(('enron.com','enron.com>')))
                            except ObjectDoesNotExist:  
                                cc=Emailadress(employee_id=None, emailadress_id=cc, interne=cc.endswith(('enron.com','enron.com>')))
                                cc.save()
            
                            c=Cc(emailadress_id=cc,mail_id=m)
                            c.save()

        else : ListemailSQL(osp.join(path,file),i)
     
if __name__=='__main__': 
    ListemailSQL()