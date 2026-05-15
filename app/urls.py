from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('produtos/', views.produtos_view, name='produtos'),
    path('minha-conta/', views.dashboard_view, name='dashboard'),
    path('atendimento/', views.atendimento_view, name='atendimento'),
]