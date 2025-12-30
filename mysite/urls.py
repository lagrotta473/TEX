from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from store.views import ProductViewSet, OrderViewSet # Importe o OrderViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet) # Nova rota de Vendas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]