from rest_framework import serializers
from django.db import transaction
from .models import Product, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'inventory_quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), 
        source='product'
    )
    
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'price_at_moment']
        read_only_fields = ['price_at_moment'] 

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'payment_method', 'total_amount', 'status', 'items']
        read_only_fields = ['total_amount', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # INÍCIO DA TRANSAÇÃO (Tudo ou Nada)
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            total_acumulado = 0
            
            for item in items_data:
                product = item['product']
                quantity = item['quantity']
                price = product.price # Snapshot do preço

                # --- LÓGICA DE PROTEÇÃO DE ESTOQUE ---
                
                # 1. Validação (Trava de Segurança)
                if product.inventory_quantity < quantity:
                    # Isso força o Rollback. A venda é cancelada e nada é salvo.
                    raise serializers.ValidationError({
                        "error": f"Estoque insuficiente para '{product.title}'. Disponível: {product.inventory_quantity}, Solicitado: {quantity}"
                    })

                # 2. Criação do Item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_moment=price
                )
                
                # 3. Baixa de Estoque (Ação Física)
                product.inventory_quantity -= quantity
                product.save() # Importante: Sem o save(), a subtração fica só na memória RAM
                
                total_acumulado += price * quantity
            
            # Finaliza o cabeçalho
            order.total_amount = total_acumulado
            order.save()
            
            return order