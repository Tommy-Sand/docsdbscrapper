#from django.db import models
from djongo import models
# Create your models here.

class pair(models.Model):
    date = models.CharField(max_length=50)
    num = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def __getitem__(self, name):
        return getattr(self, name)



class lecture(models.Model):
    Lecture = models.CharField(max_length=50)
    Instructor  = models.CharField(max_length=100)
    Cap = models.ArrayField(
        model_container = pair,
    )
    Reg = models.ArrayField(
        model_container = pair,
    )
    With = models.ArrayField(
        model_container = pair,
    )
    Cur = models.ArrayField(
        model_container = pair,
    )
    Combd = models.ArrayField(
        model_container = pair,
    )
    class Meta:
        abstract = True

    def __getitem__(self, name):
        return getattr(self, name)

class mostrecent(models.Model):
    Lecture = models.CharField(max_length=50)
    Cap = models.IntegerField(default=0)
    Reg = models.IntegerField(default=0)
    With = models.IntegerField(default=0)
    Cur = models.IntegerField(default=0)
    Combd = models.IntegerField(default=0)
    class Meta:
        abstract = True

    def __getitem__(self, name):
        return getattr(self, name)

class course(models.Model):
    cid = models.CharField(max_length=10)
    cname = models.CharField(max_length=50)
    
    lectures = models.ArrayField(
        model_container = lecture,
    )
    most_recent = models.ArrayField(
        model_container = mostrecent,
    )

    class Meta:
        abstract = True
    
    def __getitem__(self, name):
        return getattr(self, name)

class semester(models.Model):
    _id = models.ObjectIdField()
    link = models.CharField(max_length=200)
    sem_name = models.CharField(max_length=100)
    courses = models.ArrayField(
        model_container = course,
   )

class etag(models.Model):
    _id = models.ObjectIdField()
    link = models.CharField(max_length=200)
    etag = models.CharField(max_length=100)