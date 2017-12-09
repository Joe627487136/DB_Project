from django.db import models
from django.contrib import admin
# Create your models here.
import MySQLdb

class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

class Check_Account(models.Model):
    mysql_response = models.CharField(max_length=50)


class DB_Connection(models.Model):
    host = "localhost"
    user = "root"
    pwd = "zhouxuexuan123"
    db = "Django_Bookstore"
    charset = "utf8"

class Comment_Book_ID_Holder(models.Model):
    book_id = ""
    book_id_for_comment=""

def __unicode__(self):
    return self.username
