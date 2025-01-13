from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario, Evento
import json
from datetime import date, time
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

class UsuarioTests(TestCase):
    def setUp(self):
        """Configuração inicial para os testes de Usuario"""
        self.client = Client()

        # Criando uma imagem em memória para simular o upload
        image = BytesIO()
        Image.new('RGB', (100, 100), color='blue').save(image, 'JPEG')
        image.seek(0)
        uploaded_image = SimpleUploadedFile("test_image.jpg", image.getvalue(), content_type="image/jpeg")

        # Criando o usuário com uma imagem
        self.usuario = Usuario.objects.create(
            nome="João",
            sobrenome="Silva",
            username="joaosilva",
            senha="senha123",
            imagem=uploaded_image
    )

    def test_criar_usuario(self):
        """Testa a criação de um usuário"""
        self.assertEqual(self.usuario.nome, "João")
        self.assertEqual(self.usuario.sobrenome, "Silva")
        self.assertEqual(self.usuario.username, "joaosilva")
        self.assertEqual(str(self.usuario), "João Silva")

    def test_cadastrar_usuario_com_username_repetido(self):
        """Testa o cadastro de usuário com username duplicado"""
        data = {
            "nome": "Carlos",
            "sobrenome": "Almeida",
            "username": "joaosilva",  # Username já existente
            "senha": "senha789"
        }
        response = self.client.post(
            reverse('cadastrar_usuario'),
            data=data,
            format='multipart'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("erro", response.json())
        self.assertEqual(response.json()["erro"], "Nome de usuário já existe.")

    def test_listar_usuario_view(self):
        """Testa o endpoint de listagem de usuários"""
        response = self.client.get(reverse('listar_usuarios'))
        self.assertEqual(response.status_code, 200)
        usuarios = json.loads(response.content)
        self.assertEqual(len(usuarios), 1)
        self.assertEqual(usuarios[0]['nome'], "João")

def test_criar_usuario_imagem(self):
    """Testa a criação de um usuário com imagem"""

    # Criando uma imagem em memória para simular o upload
    image = BytesIO()
    Image.new('RGB', (100, 100), color='green').save(image, 'JPEG')
    image.seek(0)
    uploaded_image = SimpleUploadedFile("test_user_image.jpg", image.getvalue(), content_type="image/jpeg")

    # Dados do usuário
    data = {
        "nome": "Maria",
        "sobrenome": "Santos",
        "username": "mariasantos",
        "senha": "senha456",
        "imagem": uploaded_image
    }

    # Envia a requisição POST para criar o usuário
    response = self.client.post(
        reverse('cadastrar_usuario'),
        data=data,
        format="multipart"  # Formato necessário para envio de arquivos
    )

    # Verificação da resposta
    self.assertEqual(response.status_code, 201)
    response_data = response.json()
    self.assertIn("mensagem", response_data)
    self.assertEqual(response_data["mensagem"], "Usuário cadastrado com sucesso!")
    self.assertEqual(response_data["username"], "mariasantos")
    self.assertIsNotNone(response_data["imagem"], "A imagem deveria ser salva e retornar uma URL.")

    # Verifica se o usuário foi salvo no banco de dados
    usuario = Usuario.objects.get(username="mariasantos")
    self.assertEqual(usuario.nome, "Maria")
    self.assertEqual(usuario.sobrenome, "Santos")
    self.assertEqual(usuario.username, "mariasantos")
    self.assertIsNotNone(usuario.imagem, "A imagem deveria estar salva no banco de dados.")
    self.assertTrue(usuario.imagem.name.startswith("usuarios/"), "A imagem não foi salva no diretório correto.")
    
def test_listar_usuarios_view(self):
        """Testa o endpoint de listagem de todos os usuários"""

        # Criar múltiplos usuários para o teste
        Usuario.objects.create(
            nome="Maria",
            sobrenome="Santos",
            username="mariasantos",
            senha="senha456"
        )
        Usuario.objects.create(
            nome="Carlos",
            sobrenome="Almeida",
            username="carlosalmeida",
            senha="senha789"
        )

        # Requisição para listar todos os usuários
        response = self.client.get(reverse('listar_usuarios'))
        self.assertEqual(response.status_code, 200)
        usuarios = json.loads(response.content)
        
        # Certificar-se de que todos os usuários foram retornados
        self.assertEqual(len(usuarios), 3)  # Incluindo o usuário criado no setUp
        self.assertEqual(usuarios[0]['nome'], "João")
        self.assertEqual(usuarios[1]['nome'], "Maria")
        self.assertEqual(usuarios[2]['nome'], "Carlos")

def test_login_usuario(self):
    """Testa o endpoint de login de um usuário"""

    # Cenário 1: Login bem-sucedido
    data_login_sucesso = {
        "username": "joaosilva",
        "senha": "senha123"
    }
    response_sucesso = self.client.post(
        reverse('login_usuario'),
        data=json.dumps(data_login_sucesso),
        content_type='application/json'
    )

    self.assertEqual(response_sucesso.status_code, 200)
    response_data = response_sucesso.json()
    self.assertIn("mensagem", response_data)
    self.assertEqual(response_data["mensagem"], "Login realizado com sucesso!")
    self.assertEqual(response_data["username"], "joaosilva")
    self.assertEqual(response_data["nome"], "João")
    self.assertEqual(response_data["sobrenome"], "Silva")
    self.assertIsNone(response_data["imagem"])  # Nenhuma imagem foi adicionada no setup

    # Cenário 2: Login com senha incorreta
    data_senha_incorreta = {
        "username": "joaosilva",
        "senha": "senha_errada"
    }
    response_senha_incorreta = self.client.post(
        reverse('login_usuario'),
        data=json.dumps(data_senha_incorreta),
        content_type='application/json'
    )

    self.assertEqual(response_senha_incorreta.status_code, 401)
    self.assertIn("erro", response_senha_incorreta.json())
    self.assertEqual(response_senha_incorreta.json()["erro"], "Usuário ou senha incorretos.")

    # Cenário 3: Login com username inexistente
    data_usuario_inexistente = {
        "username": "usuario_inexistente",
        "senha": "qualquer_senha"
    }
    response_usuario_inexistente = self.client.post(
        reverse('login_usuario'),
        data=json.dumps(data_usuario_inexistente),
        content_type='application/json'
    )

    self.assertEqual(response_usuario_inexistente.status_code, 401)
    self.assertIn("erro", response_usuario_inexistente.json())
    self.assertEqual(response_usuario_inexistente.json()["erro"], "Usuário ou senha incorretos.")

    # Cenário 4: Login com dados faltando
    data_faltando_username = {"senha": "senha123"}
    response_faltando_username = self.client.post(
        reverse('login_usuario'),
        data=json.dumps(data_faltando_username),
        content_type='application/json'
    )

    self.assertEqual(response_faltando_username.status_code, 400)
    self.assertIn("erro", response_faltando_username.json())

    # Cenário 5: Método não permitido
    response_metodo_nao_permitido = self.client.get(reverse('login_usuario'))
    self.assertEqual(response_metodo_nao_permitido.status_code, 405)
    self.assertEqual(response_metodo_nao_permitido.json()["erro"], "Método não permitido")

def test_listar_usuarios_json_view(self):
    """Testa o endpoint de listagem de todos os usuários em formato JSON"""

    # Criação de usuários adicionais com caracteres especiais no nome
    Usuario.objects.create(
        nome="José",
        sobrenome="da Silva",
        username="jose.silva",
        senha="senha123"
    )
    Usuario.objects.create(
        nome="Mária",
        sobrenome="Oliveira",
        username="maria.oliveira",
        senha="senha456"
    )

    # Requisição para o endpoint
    response = self.client.get(reverse('listar_usuarios_json'))

    # Verifica se o status da resposta é 200 (OK)
    self.assertEqual(response.status_code, 200)

    # Converte o conteúdo da resposta em JSON
    usuarios_data = response.json()

    # Verifica se o número de usuários está correto
    self.assertEqual(len(usuarios_data), 3)  # Inclui o usuário criado no setUp

    # Verifica os dados dos usuários
    self.assertEqual(usuarios_data[0]['nome'], "João")
    self.assertEqual(usuarios_data[0]['sobrenome'], "Silva")

    self.assertEqual(usuarios_data[1]['nome'], "José")
    self.assertEqual(usuarios_data[1]['sobrenome'], "da Silva")

    self.assertEqual(usuarios_data[2]['nome'], "Mária")
    self.assertEqual(usuarios_data[2]['sobrenome'], "Oliveira")


class EventoTests(TestCase):
    def setUp(self):
        """Configuração inicial para os testes de Evento"""
        self.client = Client()
        self.evento = Evento.objects.create(
            nome="Workshop Python",
            data=date(2025, 1, 15),
            horario=time(14, 30),
            tipo="presencial",
            local="Centro de Convenções",
            link="https://evento.com",
            descricao="Workshop sobre Python"
        )

    def test_cadastrar_evento_view(self):
        """Testa o endpoint de cadastro de evento"""
        data = {
            "nome": "Curso Django",
            "data": "2025-02-01",
            "horario": "15:00:00",
            "tipo": "online",
            "local": "Zoom",
            "link": "https://zoom.com/meeting",
            "descricao": "Curso intensivo de Django",
            "preco": "100.00"
        }

        # Simular envio com 'multipart/form-data'
        response = self.client.post(
            reverse('cadastrar_evento'),
            data,  # Envio direto dos dados como dicionário
            format="multipart"  # Especificar envio no formato multipart
        )

        # Depuração para verificar resposta do servidor
        print("Status Code:", response.status_code)
        print("Response Content:", response.content.decode())

        # Verificar se o evento foi criado corretamente
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Evento.objects.filter(nome="Curso Django").exists())

    def test_listar_eventos_view(self):
        """Testa o endpoint de listagem de eventos"""
        response = self.client.get(reverse('listar_eventos'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['eventos']), 1)
        self.assertEqual(data['eventos'][0]['nome'], "Workshop Python")

    def test_listar_eventos_com_busca(self):
        """Testa a funcionalidade de busca na listagem de eventos"""
        response = self.client.get(
            reverse('listar_eventos'),
            {'nome': 'Python'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['eventos']), 1)
        self.assertEqual(data['eventos'][0]['nome'], "Workshop Python")


class HomeViewTests(TestCase):
    def setUp(self):
        """Configuração inicial para os testes da view home"""
        self.client = Client()

    def test_home_view(self):
        """Testa se a página inicial está carregando corretamente"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend da Agenda Tech")
        self.assertContains(response, "Cadastrar Usuário")
        self.assertContains(response, "Listar Eventos")
