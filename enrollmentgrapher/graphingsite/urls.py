from django.urls import path, include

from . import views

app_name = "graphingsite"
urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit, name='submit')
]