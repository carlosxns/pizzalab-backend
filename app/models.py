from django.db import models

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'cliente'


class Produto(models.Model):
    id_produto = models.AutoField(primary_key=True)
    nome_pizza = models.CharField(max_length=100)
    tamanho = models.CharField(max_length=50, null=True, blank=True)
    preco_base = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nome_pizza} ({self.tamanho})"

    class Meta:
        db_table = 'produto'


class Pedido(models.Model):
    STATUS_CHOICES = [
        ('Recebido', 'Recebido'),
        ('Em preparo', 'Em preparo'),
        ('Saiu para entrega', 'Saiu para entrega'),
        ('Entregue', 'Entregue'),
    ]

    id_pedido = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='id_cliente')
    data_pedido = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Recebido')

    def __str__(self):
        return f"Pedido #{self.id_pedido} - Cliente: {self.id_cliente.nome}"

    class Meta:
        db_table = 'pedido'


class ItemPedido(models.Model):
    id_item = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE, db_column='id_pedido')
    id_produto = models.ForeignKey(Produto, on_delete=models.RESTRICT, db_column='id_produto')
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.id_produto.nome_pizza} (Pedido #{self.id_pedido.id_pedido})"

    class Meta:
        db_table = 'item_pedido'
