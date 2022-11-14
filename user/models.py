from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserType(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=50,primary_key=True)
    user_type = models.CharField(max_length=20)
    user_balance = models.IntegerField()

    def __str__(self):
        return str(self.user_id)

class Trasaction(models.Model):
    user_name = models.ForeignKey(UserType, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.IntegerField()
    request_type = models.CharField(max_length=30)
    balance = models.IntegerField()
    remarks = models.CharField(max_length=50)

    def __str__(self):
        return str(self.user_name)

class Request(models.Model):
    req_id = models.AutoField(primary_key=True)
    user_name = models.ForeignKey(UserType, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.IntegerField()
    requested_by = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    action = models.CharField(max_length=20,null=True)

    def __str__(self):
        return str(self.req_id)
