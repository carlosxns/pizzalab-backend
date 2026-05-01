from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # O 'api/' significa que todas as rotas do seu app terão /api/ antes.
    # Exemplo: localhost:8000/api/produtos/
    path('api/', include('app.urls')), 
]