from django.urls import path, include

from . import views

app_name = "graphingsite"
urlpatterns = [
    path('', views.index, name='index'),
    path("submit_s/", views.submit_s, name = "submit_s"),
    path("submit_s_c/", views.submit_s_c, name = "submit_s_c"),
    path("submit_s_c_l/", views.submit_s_c_l, name= "submit_s_c_l")
]