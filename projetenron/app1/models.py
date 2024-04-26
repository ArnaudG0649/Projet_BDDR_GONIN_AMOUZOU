from django.db import models

# Create your models here.
class Employee(models.Model):
    employee_id=models.IntegerField(unique=True,primary_key=True)
    lastname=models.CharField(max_length=100)
    firstname=models.CharField(max_length=100)
    category=models.CharField(max_length=100,null=True)
    mailbox=models.CharField(max_length=100)
    def __str__(self):
      return f"{self.employee_id} {self.lastname} {self.firstname} {self.category} {self.mailbox}"
    def __repr__(self):
      return f"{self.employee_id} {self.lastname} {self.firstname} {self.category} {self.mailbox}"
  
class Emailadress(models.Model):
    emailadress_id=models.CharField(unique=True,max_length=200,primary_key=True)
    employee_id=models.ForeignKey(Employee, on_delete=models.CASCADE,null=True)
    interne=models.BooleanField()
    def __str__(self):
      return f"{self.emailadress_id} {self.employee_id}  {self.interne}"
    def __repr__(self):
      return f"{self.emailadress_id} {self.employee_id}  {self.interne}"
  
class Mail(models.Model) : 
    mail_id=models.CharField(unique=True,max_length=200,primary_key=True)
    emailadress_id=models.ForeignKey(Emailadress, on_delete=models.CASCADE)
    subject=models.CharField(max_length=200,null=True)
    timedate=models.DateTimeField()
    path=models.CharField(max_length=1000)
    def __str__(self):
      return f"{self.mail_id} {self.emailadress_id} {self.subject} {self.timedate} {self.path}"
    def __repr__(self):
      return f"{self.mail_id} {self.emailadress_id} {self.subject} {self.timedate} {self.path}"
    
class To(models.Model) : 
    emailadress_id=models.ForeignKey(Emailadress, on_delete=models.CASCADE)
    mail_id=models.ForeignKey(Mail, on_delete=models.CASCADE)
    
class Cc(models.Model) : 
    emailadress_id=models.ForeignKey(Emailadress, on_delete=models.CASCADE)
    mail_id=models.ForeignKey(Mail, on_delete=models.CASCADE)
    
# class Re(models.Model) :
#     remail_id=models.CharField(unique=True,max_length=200,primary_key=True)
#     mail_id=models.ForeignKey(Mail, on_delete=models.CASCADE)
    