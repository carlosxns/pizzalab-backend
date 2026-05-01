from django.urls import path
from . import views
from app.views import cadastrar_usuario

urlpatterns = [
    # Nossa nova rota de Login
    path('login/', views.login_view, name='login'),
    
    # Rotas do CRUD
    path('produtos/', views.gerenciar_produtos, name='produtos_lista'),
    path('produtos/<int:id>/', views.gerenciar_produtos, name='produtos_detalhe'),

   path('cadastro/', cadastrar_usuario, name='cadastrar_usuario'), 
]