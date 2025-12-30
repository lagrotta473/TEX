from rest_framework import serializers
from django.db import transaction # Importante: A trava de segurança
from .models import Product, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'barcode', 'inventory_quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    # Input: O Front manda apenas o ID do produto
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), 
        source='product'
    )
    
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price_at_moment']
        # price_at_moment é read_only por padrão na criação via lógica interna, 
        # mas deixamos aqui para ver no retorno.
        read_only_fields = ['price_at_moment'] 

class OrderSerializer(serializers.ModelSerializer):
    # Nested Relationship: Esperamos uma lista de itens dentro do pedido
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'payment_method', 'total_amount', 'status', 'items']
        read_only_fields = ['total_amount', 'created_at']

    def create(self, validated_data):
        # 1. Separa os itens do cabeçalho
        items_data = validated_data.pop('items')

        # 2. Inicia o Bloco Atômico (Tudo ou Nada)
        with transaction.atomic():
            # Cria a Venda
            order = Order.objects.create(**validated_data)
            
            total_acumulado = 0
            
            # Cria os Itens
            for item in items_data:
                product = item['product']
                quantity = item['quantity']
                price = product.price # Pega o preço ATUAL do cadastro

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_moment=price
                )
                
                total_acumulado += price * quantity
            
            # Atualiza o total da venda no final
            order.total_amount = total_acumulado
            order.save()
            
            return order