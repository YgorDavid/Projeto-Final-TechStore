from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('produtos/', views.produtos_view, name='produtos'),
    
    # Rota do Business Intelligence - Acesso Restrito
    path('dashboard-bi/', views.dashboard_bi_view, name='dashboard_bi'),
    path('bi/logistica/', views.dashboard_logistica_view, name='dashboard_logistica'),
]