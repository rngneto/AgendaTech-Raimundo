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
