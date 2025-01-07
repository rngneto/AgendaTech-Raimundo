import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Usuario, Evento
from django.conf import settings
from django.db import connection
from django.contrib.auth.hashers import check_password
from agenda.models import Usuario, Evento
from .serializers import UsuarioSerializer, EventoSerializer
from PIL import Image
import json

ALLOWED_FORMATS = ['PNG', 'JPEG', 'JPG']
MAX_WIDTH, MAX_HEIGHT = 1920, 1080

def home(request):
    """Página inicial do backend com links estilizados para os endpoints"""
    links = [
        {"nome": "Teste", "url": reverse('teste')},
        {"nome": "Cadastrar Usuário", "url": reverse('cadastrar_usuario')},
        {"nome": "Listar Usuários", "url": reverse('listar_usuarios')},
        {"nome": "Listar Usuários (JSON)", "url": reverse('listar_usuarios_json')},
        {"nome": "Cadastrar Evento", "url": reverse('cadastrar_evento')},
        {"nome": "Listar Eventos", "url": reverse('listar_eventos')},       
    ]
    html_content = """
    <html>
    <head>
        <title>Backend da Agenda Tech</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            h1 {
                color: #142f68;
                text-align: center;
            }
            ul {
                list-style: none;
                padding: 0;
            }
            li {
                margin: 10px 0;
            }
            a {
                text-decoration: none;
                color: white;
                background-color: #142f68;
                padding: 10px 15px;
                border-radius: 5px;
                display: inline-block;
                transition: background-color 0.3s;
            }
            a:hover {
                background-color: #0d2145;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                text-align: center;
            }
            .clear-btn {
                color: white;
                background-color: red;
                padding: 10px 15px;
                border-radius: 5px;
                text-decoration: none;
                display: inline-block;
                transition: background-color 0.3s;
            }
            .clear-btn:hover {
                background-color: darkred;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Bem-vindo ao Backend da Agenda Tech!</h1>
            <ul>
    """
    for link in links:
        html_content += f'<li><a href="{link["url"]}">{link["nome"]}</a></li>'
    html_content += """
            </ul>
            <form method="post" action="/limpar_bd/">
                <button type="submit" class="clear-btn" onclick="return confirm('Tem certeza que deseja limpar o banco de dados?')">Limpar Banco de Dados</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

def teste(request):
    """Endpoint de teste para verificar o funcionamento do backend"""
    data = {
        'mensagem': 'Backend está funcionando e recebendo requisições do frontend!'
    }
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def cadastrar_usuario(request):
    """Cadastra um novo usuário com imagem"""
    if request.method == 'POST':
        try:
            # Verifica se há uma imagem enviada no request
            imagem = request.FILES.get('imagem')
            
            # Converte o corpo da requisição em JSON
            dados = request.POST

            # Verifica se o username já existe
            if Usuario.objects.filter(username=dados.get('username')).exists():
                return JsonResponse({"erro": "Nome de usuário já existe."}, status=400, json_dumps_params={'ensure_ascii': False})

            # Cria o usuário com os dados fornecidos
            usuario = Usuario.objects.create(
                nome=dados.get('nome'),
                sobrenome=dados.get('sobrenome'),
                username=dados.get('username'),
                senha=dados.get('senha'),  # Apenas armazena a senha diretamente
                imagem=imagem  # Armazena a imagem se fornecida
            )
            return JsonResponse({
                "mensagem": "Usuário cadastrado com sucesso!",
                "username": usuario.username,
                "imagem": usuario.imagem.url if usuario.imagem else None
            }, status=201, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({"erro": f"Erro ao cadastrar usuário: {str(e)}"}, status=400, json_dumps_params={'ensure_ascii': False})
    return JsonResponse({"erro": "Método não permitido"}, status=405, json_dumps_params={'ensure_ascii': False})

@api_view(['GET'])
def listar_usuarios(request):
    """Lista usuários cadastrados"""
    try:
        usuarios = Usuario.objects.all()
        usuarios_serializados = [
            {
                "id": usuario.id,
                "nome": usuario.nome,
                "sobrenome": usuario.sobrenome,
                "username": usuario.username,
                "imagem": usuario.imagem.url if usuario.imagem else None,
            }
            for usuario in usuarios
        ]
        return JsonResponse(usuarios_serializados, safe=False, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"erro": f"Erro ao listar usuários: {str(e)}"}, status=400)


@api_view(['POST'])
def cadastrar_evento(request):
    """Cadastra um novo evento"""
    try:
        # Captura os campos obrigatórios
        nome = request.POST.get('nome')
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        tipo = request.POST.get('tipo')
        local = request.POST.get('local')
        link = request.POST.get('link')
        descricao = request.POST.get('descricao')
        preco = request.POST.get('preco')
        imagem = request.FILES.get('imagem')

        # Validar os campos obrigatórios individualmente
        if not nome:
            return JsonResponse({"erro": "O campo 'nome' é obrigatório."}, status=400)
        if not data:
            return JsonResponse({"erro": "O campo 'data' é obrigatório."}, status=400)
        if not horario:
            return JsonResponse({"erro": "O campo 'horário' é obrigatório."}, status=400)
        if not tipo:
            return JsonResponse({"erro": "O campo 'tipo' é obrigatório."}, status=400)
        if not local:
            return JsonResponse({"erro": "O campo 'local' é obrigatório."}, status=400)
        if not link:
            return JsonResponse({"erro": "O campo 'link' é obrigatório."}, status=400)
        if not descricao:
            return JsonResponse({"erro": "O campo 'descrição' é obrigatório."}, status=400)
        if preco is None:
            return JsonResponse({"erro": "O campo 'preço' é obrigatório."}, status=400)

        # Validar preço
        try:
            preco = float(preco)
            if preco < 0:
                return JsonResponse({"erro": "O preço não pode ser negativo."}, status=400)
        except ValueError:
            return JsonResponse({"erro": "O preço deve ser um número válido."}, status=400)
        # Validar formato e dimensões da imagem (se fornecida)
        if imagem:
            try:
                with Image.open(imagem) as img:
                    if img.format.upper() not in ALLOWED_FORMATS:
                        return JsonResponse({"erro": "Formato de imagem não suportado. Use JPEG ou PNG."}, status=400)
                    if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
                        return JsonResponse(
                            {"erro": f"Imagem excede as dimensões permitidas: {MAX_WIDTH}x{MAX_HEIGHT}."}, 
                            status=400
                        )
            except Exception as e:
                return JsonResponse({"erro": f"Erro ao processar a imagem: {str(e)}"}, status=400)

        # Criar o evento no banco de dados
        evento = Evento.objects.create(
            nome=nome,
            data=data,
            horario=horario,
            tipo=tipo,
            local=local,
            link=link,
            descricao=descricao,
            preco=preco,
            imagem=imagem
        )

        return JsonResponse({"mensagem": "Evento cadastrado com sucesso!", "id": evento.id}, status=201)

    except Exception as e:
        return JsonResponse({"erro": f"Erro interno ao cadastrar evento: {str(e)}"}, status=500)
   
def listar_eventos(request):
    """Lista eventos com suporte a paginação"""
    try:
        eventos = Evento.objects.all().order_by('data')
        paginator = Paginator(eventos, 12)  # Paginação: 12 eventos por página
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        eventos_serializados = [
            {
                "id": evento.id,
                "nome": evento.nome,
                "data": evento.data.strftime('%Y-%m-%d') if evento.data else None,
                "horario": evento.horario.strftime('%H:%M') if evento.horario else None,
                "tipo": evento.tipo,
                "local": evento.local,
                "imagem": evento.imagem.url if evento.imagem else None,
                "link": evento.link,
                "preco": evento.preco,
                "descricao": evento.descricao,                
            }
            for evento in page_obj.object_list
        ]

        return JsonResponse({
            "eventos": eventos_serializados,
            "pagina_atual": page_obj.number,
            "total_paginas": paginator.num_pages,
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"erro": f"Erro ao listar eventos: {str(e)}"}, status=400)

def listar_usuarios_json(request):
    """Lista todos os usuários com suporte a caracteres especiais"""
    try:
        usuarios = Usuario.objects.all()
        usuarios_data = [
            {'id': u.id, 'nome': u.nome, 'sobrenome': u.sobrenome}
            for u in usuarios
        ]
        return JsonResponse(usuarios_data, safe=False, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({"erro": f"Erro ao listar usuários: {str(e)}"}, status=400)

@csrf_exempt
def limpar_bd(request):
    if request.method == 'POST':
        try:
            # Apagar todos os registros das tabelas
            Usuario.objects.all().delete()
            Evento.objects.all().delete()

            # Reiniciar sequência de IDs
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='agenda_usuario';")
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='agenda_evento';")

            # Caminhos para as pastas de imagens
            eventos_path = os.path.join(settings.MEDIA_ROOT, 'eventos')
            usuarios_path = os.path.join(settings.MEDIA_ROOT, 'usuarios')

            # Função para excluir todos os arquivos em uma pasta
            def limpar_pasta(caminho):
                if os.path.exists(caminho):
                    for arquivo in os.listdir(caminho):
                        arquivo_path = os.path.join(caminho, arquivo)
                        if os.path.isfile(arquivo_path):
                            os.remove(arquivo_path)

            # Limpar pastas de imagens
            limpar_pasta(eventos_path)
            limpar_pasta(usuarios_path)

            return JsonResponse({"mensagem": "Banco de dados e arquivos limpos com sucesso!"}, status=200)
        except Exception as e:
            return JsonResponse({"erro": f"Erro ao limpar o banco: {str(e)}"}, status=400)
    return JsonResponse({"erro": "Método não permitido"}, status=405)

@csrf_exempt
def login_usuario(request):
    """Realiza login de um usuário"""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            username = dados.get('username')
            senha = dados.get('senha')

            # Busca o usuário pelo username
            usuario = Usuario.objects.filter(username=username).first()

            # Compara a senha fornecida com a armazenada
            if usuario and usuario.senha == senha:
                return JsonResponse({
                    "mensagem": "Login realizado com sucesso!",
                    "username": usuario.username,
                    "nome": usuario.nome,
                    "sobrenome": usuario.sobrenome,
                    "imagem": usuario.imagem.url if usuario.imagem else None
                }, status=200, json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({"erro": "Usuário ou senha incorretos."}, status=401, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({"erro": f"Erro ao realizar login: {str(e)}"}, status=400, json_dumps_params={'ensure_ascii': False})
    return JsonResponse({"erro": "Método não permitido"}, status=405, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def editar_perfil(request):
    """Edita o perfil do usuário"""
    if request.method == 'POST':
        try:
            # Obtém os dados enviados na requisição
            dados = json.loads(request.body)
            username = dados.get('username')

            if not username:
                return JsonResponse({"erro": "Nome de usuário não fornecido."}, status=400, json_dumps_params={'ensure_ascii': False})

            # Verifica se o usuário existe
            usuario = Usuario.objects.filter(username=username).first()
            if not usuario:
                return JsonResponse({"erro": "Usuário não encontrado."}, status=404, json_dumps_params={'ensure_ascii': False})

            # Atualiza os campos
            novo_nome = dados.get('nome')
            novo_sobrenome = dados.get('sobrenome')
            novo_username = dados.get('novo_username')

            if novo_nome:
                usuario.nome = novo_nome

            if novo_sobrenome:
                usuario.sobrenome = novo_sobrenome

            # Verifica se o novo username já está em uso
            if novo_username and novo_username != usuario.username:
                if Usuario.objects.filter(username=novo_username).exists():
                    return JsonResponse({"erro": "Nome de usuário já está em uso."}, status=400, json_dumps_params={'ensure_ascii': False})
                usuario.username = novo_username

            usuario.save()

            return JsonResponse({
                "mensagem": "Perfil atualizado com sucesso!",
                "usuario": {
                    "nome": usuario.nome,
                    "sobrenome": usuario.sobrenome,
                    "username": usuario.username
                }
            }, status=200, json_dumps_params={'ensure_ascii': False})
        except json.JSONDecodeError:
            return JsonResponse({"erro": "Dados enviados em formato inválido."}, status=400, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({"erro": f"Erro ao editar perfil: {str(e)}"}, status=500, json_dumps_params={'ensure_ascii': False})
    return JsonResponse({"erro": "Método não permitido."}, status=405, json_dumps_params={'ensure_ascii': False})