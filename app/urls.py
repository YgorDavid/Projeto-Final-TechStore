from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('logout/', views.logout_view, name='logout'),
    path('produtos/', views.produtos_view, name='produtos'),
    path('minha-conta/', views.dashboard_view, name='dashboard'),
    # path('produto/<int:pk>/', views.detalhe_produto_view, name='detalhe_produto'),
    # path('produto/<int:produto_id>/avaliar/', views.avaliar_produto, name='avaliar_produto'),
]