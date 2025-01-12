import os
import json
import shutil
import zipfile
from PIL import Image

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Usuario, Evento, ListaDesejos
from .serializers import UsuarioSerializer, EventoSerializer


ALLOWED_FORMATS = ['PNG', 'JPEG', 'JPG', 'WEBP', 'GIF', 'BMP', 'TIFF']  # Mais formatos suportados
MAX_WIDTH, MAX_HEIGHT = 10000, 10000  # Dimensões aumentadas

def home(request):
    """Página inicial do backend com links estilizados para os endpoints"""
    links = [
        {"nome": "Teste", "url": reverse('teste')},
        {"nome": "Cadastrar Usuário", "url": reverse('cadastrar_usuario')},
        {"nome": "Listar Usuários", "url": reverse('listar_usuarios')},
        {"nome": "Listar Usuários (JSON)", "url": reverse('listar_usuarios_json')},
        {"nome": "Cadastrar Evento", "url": reverse('cadastrar_evento')},
        {"nome": "Login Usuário", "url": reverse('login_usuario')},
        {"nome": "Listar Eventos", "url": reverse('listar_eventos')},
        {"nome": "Listar Eventos por Nome", "url": reverse('listar_eventos_nome')},
        {"nome": "Editar Perfil", "url": reverse('editar_perfil')},
        {"nome": "Detalhe do Evento", "url": reverse('detalhe_evento')},
        {"nome": "Exportar Backup", "url": reverse('exportar_backup'), "class": "export-link"},
        {"nome": "Restaurar Backup", "url": reverse('restaurar_backup'), "class": "restore-link"},
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
                padding: 10px 15px;
                border-radius: 5px;
                display: inline-block;
                transition: background-color 0.3s;
                text-align: center;
                width: 200px; /* Define uma largura fixa */
            }
            a:hover {
                opacity: 0.9;
            }
            .default-link {
                background-color: #142f68;
            }
            .default-link:hover {
                background-color: #0d2145;
            }
            .export-link {
                background-color: #006400; /* Verde escuro */
            }
            .export-link:hover {
                background-color: #004d00;
            }
            .restore-link {
                background-color: #32cd32; /* Verde claro */
            }
            .restore-link:hover {
                background-color: #228b22;
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
                text-align: center;
                width: 230px; /* Define uma largura fixa */
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
        link_class = link.get("class", "default-link")
        html_content += f'<li><a href="{link["url"]}" class="{link_class}">{link["nome"]}</a></li>'
    html_content += """
            </ul>
            <form method="post" action="/api/limpar_bd/" style="display: inline-block;">
                <button type="submit" class="clear-btn" onclick="return confirm('Tem certeza que deseja limpar o banco de dados?')">
                    Limpar Banco de Dados
                </button>
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
            return JsonResponse({"erro": "O campo 'nome' é obrigatório. [Código: 001]"}, status=400)
        if not data:
            return JsonResponse({"erro": "O campo 'data' é obrigatório. [Código: 002]"}, status=400)
        if not horario:
            return JsonResponse({"erro": "O campo 'horário' é obrigatório. [Código: 003]"}, status=400)
        if not tipo:
            return JsonResponse({"erro": "O campo 'tipo' é obrigatório. [Código: 004]"}, status=400)
        if not local:
            return JsonResponse({"erro": "O campo 'local' é obrigatório. [Código: 005]"}, status=400)
        if not link:
            return JsonResponse({"erro": "O campo 'link' é obrigatório. [Código: 006]"}, status=400)
        if not descricao:
            return JsonResponse({"erro": "O campo 'descrição' é obrigatório. [Código: 007]"}, status=400)
        if preco is None:
            return JsonResponse({"erro": "O campo 'preço' é obrigatório. [Código: 008]"}, status=400)

        # Validar preço
        try:
            preco = float(preco)
            if preco < 0:
                return JsonResponse({"erro": "O preço não pode ser negativo. [Código: 009]"}, status=400)
        except ValueError:
            return JsonResponse({"erro": "O preço deve ser um número válido. [Código: 010]"}, status=400)

        # Validar formato e dimensões da imagem (se fornecida)
        if imagem:
            try:
                with Image.open(imagem) as img:
                    if img.format.upper() not in ALLOWED_FORMATS:
                        return JsonResponse(
                            {"erro": f"Formato de imagem não suportado ({img.format}). [Código: 011]"}, status=400
                        )
                    if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
                        return JsonResponse(
                            {
                                "erro": f"Imagem excede as dimensões permitidas: {MAX_WIDTH}x{MAX_HEIGHT}. [Código: 012]"
                            },
                            status=400
                        )
            except Exception as e:
                return JsonResponse({"erro": f"Erro ao processar a imagem: {str(e)} [Código: 013]"}, status=400)

        # Criar o evento no banco de dados
        try:
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
        except Exception as e:
            return JsonResponse({"erro": f"Erro ao salvar evento no banco de dados: {str(e)} [Código: 014]"}, status=500)

        return JsonResponse({"mensagem": "Evento cadastrado com sucesso!", "id": evento.id}, status=201)

    except Exception as e:
        return JsonResponse({"erro": f"Erro interno ao cadastrar evento: {str(e)} [Código: 015]"}, status=500)
  
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
    
def listar_eventos_nome(request):
    """Lista eventos com busca insensível a maiúsculas/minúsculas e espaços"""
    try:
        termo = request.GET.get('nome', '').strip()  # Remove espaços adicionais
        # Usa icontains para uma busca insensível a maiúsculas/minúsculas
        eventos = Evento.objects.filter(Q(nome__icontains=termo)).order_by('data') if termo else Evento.objects.all().order_by('data')

        paginator = Paginator(eventos, 12)  # Paginação
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
                    "id": usuario.id,  # Incluindo o ID do usuário
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

@csrf_exempt
def detalhe_evento(request):
    """Retorna os detalhes de um evento específico"""
    id = request.GET.get('id')  # Obtém o ID do evento da query string
    if not id:
        return JsonResponse({"erro": "ID do evento não fornecido."}, status=400)

    # Busca o evento ou retorna 404
    evento = get_object_or_404(Evento, id=id)

    # Serializa os dados do evento
    evento_serializado = {
        "id": evento.id,
        "nome": evento.nome,
        "data": evento.data.strftime('%Y-%m-%d') if evento.data else None,
        "horario": evento.horario.strftime('%H:%M') if evento.horario else None,
        "tipo": evento.tipo,
        "local": evento.local,
        "link": evento.link,
        "descricao": evento.descricao,
        "preco": float(evento.preco) if evento.preco else "Gratuito",
        "imagem": evento.imagem.url if evento.imagem else None,
    }

    # Retorna os dados como JSON
    return JsonResponse(evento_serializado, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def detalhe_evento_por_query(request):
    """Retorna os detalhes de um evento específico baseado na query string"""
    id = request.GET.get('id')  # Obtém o ID do evento da query string
    if not id:
        return JsonResponse({"erro": "ID do evento não fornecido."}, status=400)

    try:
        # Busca o evento ou retorna 404
        evento = get_object_or_404(Evento, id=id)

        # Serializa os dados do evento
        evento_serializado = {
            "id": evento.id,
            "nome": evento.nome,
            "data": evento.data.strftime('%Y-%m-%d') if evento.data else None,
            "horario": evento.horario.strftime('%H:%M') if evento.horario else None,
            "tipo": evento.tipo,
            "local": evento.local,
            "link": evento.link,
            "descricao": evento.descricao,
            "preco": float(evento.preco) if evento.preco else "Gratuito",
            "imagem": evento.imagem.url if evento.imagem else None,
        }

        # Retorna os dados como JSON
        return JsonResponse(evento_serializado, json_dumps_params={'ensure_ascii': False})
    except ValueError:
        return JsonResponse({"erro": "ID inválido."}, status=400)

@csrf_exempt
@api_view(['GET'])
def exportar_backup(request):
    """Exporta o banco de dados e a pasta media em um arquivo ZIP."""
    try:
        # Caminhos dos arquivos
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        media_path = os.path.join(settings.BASE_DIR, 'media')
        backup_folder = os.path.join(settings.BASE_DIR, 'backup')
        os.makedirs(backup_folder, exist_ok=True)

        # Nome do arquivo de backup
        backup_name = f"backup_{now().strftime('%Y%m%d_%H%M%S')}.zip"
        backup_path = os.path.join(backup_folder, backup_name)

        # Compactar arquivos em um ZIP
        with zipfile.ZipFile(backup_path, 'w') as backup_zip:
            backup_zip.write(db_path, 'db.sqlite3')
            for root, dirs, files in os.walk(media_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, media_path)
                    backup_zip.write(file_path, os.path.join('media', arcname))

        return FileResponse(open(backup_path, 'rb'), as_attachment=True, filename=backup_name)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@api_view(['GET', 'POST'])
def restaurar_backup(request):
    """Página para upload e restauração do backup."""
    if request.method == 'GET':
        # Renderiza um formulário HTML estilizado para envio do arquivo
        html_content = """
        <html>
        <head>
            <title>Restaurar Backup</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    margin: 0;
                    padding: 20px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
                .container {
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 30px;
                    width: 400px;
                    text-align: center;
                }
                h1 {
                    color: #142f68;
                    font-size: 24px;
                    margin-bottom: 20px;
                }
                label {
                    font-size: 16px;
                    margin-bottom: 10px;
                    display: block;
                    color: #333;
                }
                input[type="file"] {
                    padding: 10px;
                    margin: 15px 0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    width: 100%;
                }
                button {
                    background-color: #006400; /* Verde escuro */
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: background-color 0.3s;
                }
                button:hover {
                    background-color: #004d00; /* Verde mais escuro */
                }
                .success {
                    color: #006400;
                    font-weight: bold;
                }
                .error {
                    color: red;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Restaurar Backup</h1>
                <form method="POST" enctype="multipart/form-data">
                    <label for="backup">Selecione o arquivo de backup (ZIP):</label>
                    <input type="file" name="backup" id="backup" required>
                    <button type="submit">Restaurar</button>
                </form>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content)

    elif request.method == 'POST':
        try:
            # Verificar se o arquivo foi enviado
            backup_file = request.FILES.get('backup')
            if not backup_file:
                return JsonResponse({"error": "Nenhum arquivo foi enviado."}, status=400)

            # Caminhos dos arquivos
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            media_path = os.path.join(settings.BASE_DIR, 'media')

            # Criar uma pasta temporária para extração
            temp_folder = os.path.join(settings.BASE_DIR, 'temp_backup')
            os.makedirs(temp_folder, exist_ok=True)

            # Salvar o arquivo ZIP recebido
            zip_path = os.path.join(temp_folder, 'backup.zip')
            with open(zip_path, 'wb') as f:
                for chunk in backup_file.chunks():
                    f.write(chunk)

            # Extrair o arquivo ZIP
            with zipfile.ZipFile(zip_path, 'r') as backup_zip:
                backup_zip.extractall(temp_folder)

            # Substituir o banco de dados e a pasta media
            if os.path.exists(os.path.join(temp_folder, 'db.sqlite3')):
                shutil.copy2(os.path.join(temp_folder, 'db.sqlite3'), db_path)
            if os.path.exists(os.path.join(temp_folder, 'media')):
                if os.path.exists(media_path):
                    shutil.rmtree(media_path)
                shutil.copytree(os.path.join(temp_folder, 'media'), media_path)

            # Limpar arquivos temporários
            shutil.rmtree(temp_folder)

            return JsonResponse({"success": "Backup restaurado com sucesso!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
@csrf_exempt
def listar_usuario(request):
    """Exibe os dados de um usuário específico"""
    try:
        if request.method == 'POST':
            dados = json.loads(request.body)
            username = dados.get('username')  # Obtém o username enviado no body

            if not username:
                return JsonResponse({"erro": "Username não fornecido."}, status=400)

            # Busca o usuário no banco de dados
            usuario = Usuario.objects.get(username=username)

            # Retorna os dados do usuário
            usuario_data = {
                "nome": usuario.nome,
                "sobrenome": usuario.sobrenome,
                "username": usuario.username,
                "senha": usuario.senha,
                "imagem": usuario.imagem.url if usuario.imagem else None,
            }

            return JsonResponse({"usuario": usuario_data}, status=200)

        return JsonResponse({"erro": "Método não permitido. Use POST."}, status=405)
    except Usuario.DoesNotExist:
        return JsonResponse({"erro": "Usuário não encontrado."}, status=404)
    except Exception as e:
        return JsonResponse({"erro": f"Erro ao processar a solicitação: {str(e)}"}, status=500)
    
@csrf_exempt
def adicionar_a_lista(request):
    if request.method == "POST":
        try:
            # Captura os dados do corpo da requisição (JSON)
            dados = json.loads(request.body)
            usuario_id = dados.get("usuario_id")
            evento_id = dados.get("evento_id")

            print(f"ID do usuário recebido: {usuario_id}")
            print(f"ID do evento recebido: {evento_id}")

            # Certifique-se de que os IDs foram fornecidos
            if not usuario_id or not evento_id:
                return JsonResponse({"error": "IDs inválidos fornecidos."}, status=400)

            # Localiza o usuário e o evento
            usuario = get_object_or_404(Usuario, id=usuario_id)
            evento = get_object_or_404(Evento, id=evento_id)

            # Verifica se o evento já está na lista de desejos
            if ListaDesejos.objects.filter(usuario=usuario, evento=evento).exists():
                return JsonResponse({"message": "Evento já está na lista de desejos!"}, status=400)

            # Adiciona o evento à lista de desejos
            ListaDesejos.objects.create(usuario=usuario, evento=evento)
            return JsonResponse({"message": "Evento adicionado à lista de desejos!"}, status=201)
        except Exception as e:
            print(f"Erro no backend: {str(e)}")  # Log do erro no terminal
            return JsonResponse({"error": f"Erro ao adicionar à lista de desejos: {str(e)}"}, status=400)
    return JsonResponse({"error": "Método não permitido. Use POST."}, status=405)

@csrf_exempt
def listar_lista_desejos(request):
    if request.method == "GET":
        try:
            usuario_id = request.GET.get("usuario_id")
            if not usuario_id:
                return JsonResponse({"error": "Usuário não especificado."}, status=400)

            lista_desejos = ListaDesejos.objects.filter(usuario__id=usuario_id).select_related('evento')

            eventos = [
                {
                    "id": desejo.evento.id,
                    "nome": desejo.evento.nome,
                    "data": desejo.evento.data,
                    "horario": desejo.evento.horario,
                    "local": desejo.evento.local,
                    "descricao": desejo.evento.descricao,
                    "imagem": desejo.evento.imagem.url if desejo.evento.imagem else None,
                    "preco": desejo.evento.preco,
                    "tipo": desejo.evento.tipo,
                }
                for desejo in lista_desejos
            ]

            return JsonResponse({"eventos": eventos}, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({"error": f"Erro ao listar lista de desejos: {str(e)}"}, status=400)
    return JsonResponse({"error": "Método não permitido."}, status=405)