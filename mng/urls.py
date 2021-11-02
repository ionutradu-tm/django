from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('deploy/', views.deploy, name='deploy'),
    path('create_branch/', views.create_branch, name='create_branch'),
    path('functional_tests', views.functional_tests, name='functional_tests'),
    path('train', views.train, name='train'),
    path('vm_power', views.vm_power, name='vm_power'),
    path('replica', views.replica, name='replica'),
    path('debug', views.debug, name='debug'),
]
