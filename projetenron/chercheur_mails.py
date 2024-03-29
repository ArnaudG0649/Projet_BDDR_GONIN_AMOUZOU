#!/usr/bin/env python3

import re
import os 
import os.path as osp 
import datetime

import django

#'django_extensions' ##Pour éxecuter la commande au projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetenron.settings') 
django.setup()

from app1.models import Employee,Emailadress,Mail,To,Cc,Re

from django.core.exceptions import ObjectDoesNotExist

os.getcwd()
os.listdir(os.getcwd()) 
#osp.join
#osp.isfile(f)
#osp.basename(os.getcwd())


class Mailobj() : 
    
    def __init__(self,path) : 
        self.path=path[len(osp.join(os.getcwd(),"maildir/"))-1:] #Chemin qui commence après le "maildir/"
         
        try : 
            with open(path,"r") as file :
                Lignes=[ligne for ligne in file]
        except UnicodeDecodeError :
            with open(path,"rb") as file :
                Lignes=str(file.read()).split(r'\n')
        #self.lignes=Lignes
        
        self.id=re.search(r"<(.*)>",Lignes[0]).group(1)
        
        Lmois=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

        d=Lignes[1].split(" ")[1:]
        nummois=Lmois.index(d[2])+1
        delta=datetime.timedelta(hours=-int(d[-2][2]))
        zone=datetime.timezone(delta)
        self.date=datetime.datetime(int(d[3]), nummois, int(d[1]), hour=int(d[4][:2]), minute=int(d[4][3:5]), second=int(d[4][6:]), tzinfo=zone)
        
        self.fromm=re.search(r"From: (\S*)",Lignes[2]).group(1)
        
        i=3
        if re.search(r"To: ([^(\n)]*)",Lignes[i]): 
            s=re.search(r"To: ([^(\n)]*)",Lignes[i]).group(1)
            s=re.sub(r"\s",r"",s)
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
        

def ListemailSQL(path=osp.join(os.getcwd(),"maildir")): #pa=Premier Appel
    print(path)
    for file in os.listdir(path) : 
        if osp.isfile(osp.join(path,file)) : #C'est là qu'on collecte les données du mail
            mail=Mailobj(osp.join(path,file))
            newmail=False
            
            try :  #Adresse email de l'expéditeur
                ea=Emailadress.objects.get(employee_id=None, emailadress_id=mail.fromm, interne=mail.fromm.endswith("enron.com"))
            except ObjectDoesNotExist:  
                ea=Emailadress(employee_id=None, emailadress_id=mail.fromm, interne=mail.fromm.endswith("enron.com"))
                ea.save()
            
            try :  #Table "mail"
                m=Mail.objects.get(mail_id=mail.id,emailadress_id=ea,subject=mail.subject,timedate=mail.date,path=mail.path)
            except ObjectDoesNotExist:
                newmail=True
                m=Mail(mail_id=mail.id,emailadress_id=ea,subject=mail.subject,timedate=mail.date,path=mail.path)
                m.save()
                print(f"bd alimetée avec {osp.join(os.getcwd(),'maildir',mail.path)}")
            
            if newmail : #Si le mail est nouveau
            
                if mail.to : 
                    for to in mail.to : #D'abord on regarde si l'adresse de chaque destinataire est déjà enregistrée et on le fait si ce n'est pas la cas
                            try :  
                                to=Emailadress.objects.get(employee_id=None, emailadress_id=to, interne=mail.fromm.endswith("enron.com"))
                            except ObjectDoesNotExist:  
                                to=Emailadress(employee_id=None, emailadress_id=to, interne=mail.fromm.endswith("enron.com"))
                                to.save()
                            
                            #Puis on la rajoute dans la table croisée "To"
                            t=To(emailadress_id=to,mail_id=m)
                            t.save()
                            
                if mail.cc :    
                    for cc in mail.cc :
                            try : 
                                cc=Emailadress.objects.get(employee_id=None, emailadress_id=cc, interne=mail.fromm.endswith("enron.com"))
                            except ObjectDoesNotExist:  
                                cc=Emailadress(employee_id=None, emailadress_id=cc, interne=mail.fromm.endswith("enron.com"))
                                cc.save()
            
                            c=Cc(emailadress_id=cc,mail_id=m)
                            c.save()

        else : ListemailSQL(osp.join(path,file))
        
ListemailSQL()

# L=[mail.id,mail.date,mail.path,mail.fromm,mail.to,mail.subject,mail.cc]

# try:
#     e=Employee.objects.get(employee_id=i+1, lastname=L[1].text, firstname=L[2].text, category=L[0].attrib['category'])
# except ObjectDoesNotExist:
#     e=Employee(employee_id=i+1, lastname=L[1].text, firstname=L[2].text, category=L[0].attrib['category'])
#     e.save()





# def Listemail(path=osp.join(os.getcwd(),"maildir"),Table=None,pa=True): #pa=Premier Appel
#     print(path)
#     if Table is None : Table=[]
#     for file in os.listdir(path) : 
#         if osp.isfile(osp.join(path,file)) : #C'est là qu'on collecte les données du mail
#             mail=Mail(osp.join(path,file))
#             L=[mail.id,mail.date,mail.path,mail.fromm,mail.to,mail.subject,mail.cc]
#             #print(L)
        
        
#             Table.append(L)

#         else : Listemail(osp.join(path,file),Table,False)
#     if pa : 
#         return Table
    
    
# listemail=Listemail()  


# # for i in listemail : print(i)

# for i in listemail :
#     if i[-2] and i[-2].startswith("RE:"): 
#         print(i[-2],i[2])
    
# Mail("/users/2024/ds1/122005148/Bureau/projet_BDDR/15.").fromm
# Mail("/users/2024/ds1/122005148/Bureau/projet_BDDR/15.").to
# Mail("/users/2024/ds1/122005148/Bureau/projet_BDDR/maildir/may-l/_sent_mail/32.").subject.startswith(" RE:")
# Mail("/users/2024/ds1/122005148/Bureau/projet_BDDR/15.").date

# Mail("/users/2024/ds1/122005148/Bureau/projet_BDDR/36.").cc


# Lemailcc=[l[5] for l in listemail]
# Lemaildate=[l[1] for l in listemail]
# print(Lemaildate)
# set(Lemaildate)

# path="/users/2024/ds1/122005148/Bureau/projet_BDDR/15."
# try : 
#     with open(path,"r") as file :
#         Lignes=[ligne for ligne in file]
# except UnicodeDecodeError :
#     with open(path,"rb") as file :
#         Lignes=str(file.read()).split(r'\n')

# Lmois=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# d=Lignes[1].split(" ")[1:]
# nummois=Lmois.index(d[2])+1
# delta=datetime.timedelta(hours=-int(d[-2][2]))
# zone=datetime.timezone(delta)
# dateinstance=datetime.datetime(int(d[3]), nummois, int(d[1]), hour=int(d[4][:2]), minute=int(d[4][3:5]), second=int(d[4][6:]), tzinfo=zone)

#-0800 (PST)
#-0700 (PDT)

# s=re.search(r"To: ([^(\n)]*)",Lignes[3]).group(1)
# s=re.sub(r"\s",r"",s)
# i=4
# while not bool(re.match(r'Subject:',Lignes[i])) :
#     s+=re.sub(r"\s",r"",Lignes[i])
#     i+=1
# Lto=s.split(',')

# re.search(r"([^ ]*)*",Lignes[7]).groups()


# with open("15.","r") as file : 
#     Lignes=[ligne for ligne in file]

# Lignes

# re.search(r"<(.*)>",Lignes[0]).group(1)


# # regex=re.compile(r'')
# # found=regex.search(ligne)
# # found.group()

# with open("/users/2024/ds1/122005148/Bureau/projet_BDDR/maildir/whalley-g/inbox/60.","rb") as file : 
#     Lignes=str(file.read()).split(r'\n')
# Lignes
    

















