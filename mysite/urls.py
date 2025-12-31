from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from store.views import ProductViewSet, OrderViewSet

# Configuração do Cabeçalho da Documentação
schema_view = get_schema_view(
   openapi.Info(
      title="API do Bar de Praia 🍺",
      default_version='v1',
      description="Sistema de PDV para controle de vendas e estoque.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="engenheiro@pdv.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    # Novas Rotas de Documentação
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]