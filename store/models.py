from django.db import models

class Product(models.Model):
    # UUID é melhor que ID sequencial (1, 2, 3) para segurança e distribuição de dados
    # mas para um MVP simples de loja, AutoField (padrão) serve. 
    # Vamos focar no que uma conveniência precisa:
    
    title = models.CharField(max_length=255, verbose_name="Nome do Produto")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    # Preço: max_digits=10 (até 99 milhões), decimal_places=2 (centavos)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda")
    
    # Código de barras é a chave de um PDV eficiente
    barcode = models.CharField(max_length=13, unique=True, verbose_name="Código de Barras (EAN)")
    
    # Controle de Estoque simples
    inventory_quantity = models.IntegerField(default=0, verbose_name="Qtd em Estoque")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Cadastrado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    # Dunder method (__str__): Como esse objeto aparece escrito no sistema
    def __str__(self):
        return f"{self.title} (R$ {self.price})"

    class Meta:
        ordering = ['title']
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('CREDIT', 'Cartão de Crédito'),
        ('DEBIT', 'Cartão de Débito'),
        ('PIX', 'PIX'),
        ('CASH', 'Dinheiro'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('PAID', 'Pago'),
        ('CANCELED', 'Cancelado'),
    ]

    # No futuro, aqui entraria o "Caixa" ou "Vendedor"
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data da Venda")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PAID')
    
    # Campo calculado (desnormalização controlada para performance de relatório)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Venda #{self.id} - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at'] # As vendas mais recentes aparecem primeiro
        verbose_name = "Venda"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # Se apagar o produto, não apaga a venda (Histórico)
    
    quantity = models.PositiveIntegerField(default=1)
    
    # IMPORTANTE: Gravamos o preço aqui para não sofrer alteração se o preço do produto mudar depois
    price_at_moment = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.title}"
        
    # Método auxiliar para calcular subtotal
    def get_subtotal(self):
        return self.price_at_moment * self.quantity        