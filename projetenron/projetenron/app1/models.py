from django.db import models

# Create your models here.
class Employee(models.Model):
    employee_id=models.IntegerField(unique=True,primary_key=True)
    lastname=models.CharField(max_length=(100))
    firstname=models.CharField(max_length=(100))
    category=models.CharField(max_length=(100))
    def __str__(self):
      return f"{self.employee_id} {self.lastname} {self.firstname} {self.category}"
    def __repr__(self):
      return f"{self.employee_id} {self.lastname} {self.firstname} {self.category}"
  
class Emailadress(models.Model):
    emailadress_id=models.IntegerField(unique=True,primary_key=True)
    employee_id=models.ForeignKey(Employee, on_delete=models.CASCADE)
    interne=models.BooleanField()
    def __str__(self):
      return f"{self.emailadress_id} {self.employee_id}  {self.interne}"
    def __repr__(self):
      return f"{self.emailadress_id} {self.employee_id}  {self.interne}"