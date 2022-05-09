# Generated by Django 3.1.12 on 2022-05-08 01:58

from django.db import migrations, models
import djongo.models.fields
import graphingsite.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='etag',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('link', models.CharField(max_length=200)),
                ('etag', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='semester',
            fields=[
                ('_id', djongo.models.fields.ObjectIdField(auto_created=True, primary_key=True, serialize=False)),
                ('link', models.CharField(max_length=200)),
                ('sem_name', models.CharField(max_length=100)),
                ('courses', djongo.models.fields.ArrayField(model_container=graphingsite.models.course)),
            ],
        ),
    ]
