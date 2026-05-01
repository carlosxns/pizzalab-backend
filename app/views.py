import json
import jwt
import datetime
import bleach
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Produto
from django.contrib.auth.models import User

# ---------------------------------------------------------
# 1. O "Segurança" (Proteção das rotas com JWT)
# ---------------------------------------------------------
def token_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Pega o token enviado no cabeçalho da requisição
        token = request.headers.get('Authorization')
        
        if not token:
            return JsonResponse({'error': 'Acesso negado. Token não fornecido.'}, status=401)
        
        try:
            # O padrão é enviar "Bearer <token>", então separamos a palavra Bearer
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
                
            # Verifica se o token é válido e se não expirou
            jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado. Faça login novamente.'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido.'}, status=401)
            
        return view_func(request, *args, **kwargs)
    return wrapper

# ---------------------------------------------------------
# 2. A "Bilheteria" (Rota de Login)
# ---------------------------------------------------------
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            usuario = dados.get('username')
            senha = dados.get('password')

            # Simulação de usuário para o projeto (num cenário real, consultaria o banco)
            if usuario == 'admin' and senha == 'pizzalab123':
                # Gera o Token JWT válido por 2 horas
                payload = {
                    'user': usuario,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
                }
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                
                return JsonResponse({'token': token, 'message': 'Login bem-sucedido!'})
            else:
                return JsonResponse({'error': 'Credenciais inválidas!'}, status=401)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

# ---------------------------------------------------------
# 3. Nossas rotas CRUD (Agora trancadas com @token_required)
# ---------------------------------------------------------
@csrf_exempt
@token_required  # <-- Essa linha trava a rota!
def gerenciar_produtos(request, id=None):
    # CREATE (POST)
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            nome_pizza = dados.get('nome_pizza')
            tamanho = dados.get('tamanho')
            preco_base = dados.get('preco_base')

            if not nome_pizza or not preco_base:
                return JsonResponse({'error': 'Os campos nome_pizza e preco_base são obrigatórios!'}, status=400)

            nome_limpo = bleach.clean(nome_pizza)
            tamanho_limpo = bleach.clean(tamanho) if tamanho else None

            produto = Produto.objects.create(nome_pizza=nome_limpo, tamanho=tamanho_limpo, preco_base=preco_base)
            return JsonResponse({'message': 'Produto cadastrado com sucesso!', 'produto': {'id': produto.id_produto, 'nome': produto.nome_pizza}}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # READ (GET)
    elif request.method == 'GET':
        if id:
            produto = get_object_or_404(Produto, pk=id)
            return JsonResponse({'id_produto': produto.id_produto, 'nome_pizza': produto.nome_pizza, 'tamanho': produto.tamanho, 'preco_base': str(produto.preco_base)})
        else:
            produtos = list(Produto.objects.values())
            return JsonResponse(produtos, safe=False)

    # UPDATE (PUT)
    elif request.method == 'PUT':
        if not id:
            return JsonResponse({'error': 'ID do produto é obrigatório.'}, status=400)
        try:
            dados = json.loads(request.body)
            if 'nome_pizza' in dados: dados['nome_pizza'] = bleach.clean(dados['nome_pizza'])
            if 'tamanho' in dados: dados['tamanho'] = bleach.clean(dados['tamanho'])

            linhas_afetadas = Produto.objects.filter(pk=id).update(**dados)
            if linhas_afetadas == 0:
                return JsonResponse({'error': 'Produto não encontrado!'}, status=404)
            return JsonResponse({'message': 'Produto atualizado com sucesso!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # DELETE (DELETE)
    elif request.method == 'DELETE':
        if not id:
            return JsonResponse({'error': 'ID do produto é obrigatório.'}, status=400)
        linhas_afetadas = Produto.objects.filter(pk=id).delete()
        if linhas_afetadas[0] == 0:
            return JsonResponse({'error': 'Produto não encontrado!'}, status=404)
        return JsonResponse({'message': 'Produto excluído com sucesso!'})
    
@csrf_exempt
def cadastrar_usuario(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            username = dados.get('username')
            password = dados.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Os campos username e password são obrigatórios.'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Este nome de usuário já está em uso.'}, status=400)

            # O create_user já salva a senha com hash de segurança automaticamente
            user = User.objects.create_user(username=username, password=password)
            
            return JsonResponse({'message': 'Usuário cadastrado com sucesso!', 'id': user.id}, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Método não permitido.'}, status=405)