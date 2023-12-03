from django.db import models

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(max_length=200)
    mail = models.TextField(max_length=50)
    password = models.TextField(max_length=8)
    registered = models.DateTimeField(auto_now_add=True)
    # Campos adicionais
    last_login = models.DateTimeField(null=True, blank=True)

class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField(max_length=50)
    registered = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField(max_length=50)

class Patterns(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.TextField()
    id_category = models.ForeignKey(Categories, on_delete=models.PROTECT)
    registered = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField(max_length=50)
    




    
    