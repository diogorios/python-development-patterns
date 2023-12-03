from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from .models import Users
from .models import Categories
from .models import Patterns
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
import requests
from datetime import datetime
import json
from django.contrib.auth.models import User

# Configuração do Firebase
FIREBASE_URL = "https://developer-pattern-python-default-rtdb.firebaseio.com/"

def home(request):
    return render(request,'main/home.html')

def option(request):
    return render(request,'action/option.html')

def cadCategory(request):
    response = requests.get(f'{FIREBASE_URL}/Categories/.json')
    
    if response.status_code == 200:
        categories_data = response.json()

        # Converte os dados do Firebase em uma lista de dicionários
        categories = []
        for category_id, category_data in categories_data.items():
            category = {
                'id': category_id,
                'description': category_data.get('description', ''),
            }
            categories.append(category)

        # Renderiza o template com as categorias
        return render(request, 'action/category.html', {'categories': categories})
    else:
        # Trata erros na requisição ao Firebase
        return render(request, 'error.html', {'error_message': f"Erro ao obter dados do Firebase. Código de status: {response.status_code}"})
   

def cadPattern(request):
    categories = get_categories()
    patterns = get_patterns()

    # Renderiza a página passando as categorias no contexto
    return render(request, 'action/pattern.html', {'categories': categories, 'patterns': patterns})
            
# Visão para exibir o formulário de cadastro de usuário
def cadUser(request):
    return render(request, 'user/cad_user.html')

def loginUser(request):
    return render(request,'user/login.html')

def process_login(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    
    # Recuperar todos os usuários do Firebase
    all_users_request = requests.get(f'{FIREBASE_URL}/Users.json')
    all_users_request.raise_for_status()
    all_users_data = all_users_request.json()

    # Verificar se o e-mail já existe localmente
    existing_user = next((user_data for user_data in all_users_data.values() 
                      if user_data['mail'] == email and user_data['password'] == senha), None)

    
    if existing_user:
        # Armazenar dados do usuário na sessão
        request.session['user_data'] = {
            'nome': existing_user['name'],
            'email': existing_user['mail'],
        }
        
        #login(request, user_data['mail'])
        return redirect('option')
    else:
        # Autenticação falhou
        return render(request, 'user/login.html', {'error_message': 'Credenciais inválidas'})
    
# Visão para gravar os dados de usuário no banco
def process_cadUser(request):
    #Usuário convidado, sem permissões 
    if not check_user_permissions(request):
        return HttpResponse("Usuário sem permissão", status=403)

    name = request.POST.get('nome')
    mail = request.POST.get('email')
    password = request.POST.get('senha')
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
       # Recuperar todos os usuários do Firebase
        all_users_request = requests.get(f'{FIREBASE_URL}/Users.json')
        all_users_request.raise_for_status()
        all_users_data = all_users_request.json()

        # Verificar se o e-mail já existe localmente
        existing_user = next((user_data for user_data in all_users_data.values() 
                              if user_data['mail'] == mail), None)

        if existing_user:
            # Usuário já cadastrado, não limpe os campos
            form_data = {
                'nome': name,
                'email': mail,
                'senha': password,
            }
            return render(request, 'user/cad_user.html', {'form_data': form_data, 'error_mail_duplicate': 'E-mail já cadastrado'})
        else:
            # Criar um novo usuário no Firebase
            dados = {
                'name': name,
                'mail': mail,
                'password': password,
                'registered': current_date
            }

            requisicao = requests.post(f'{FIREBASE_URL}/Users.json', data=json.dumps(dados))
            requisicao.raise_for_status()

            return redirect('home')

    except requests.exceptions.RequestException as error:
        # Trata erros na requisição para o Firebase
        print(f"Erro na requisição para o Firebase: {error}")
        return HttpResponse("Erro ao processar a requisição para o Firebase.", status=500)


def list_patterns(request):
    categories = get_categories()
    patterns = get_patterns()
    return render(request, 'action/pattern.html', {'categories': categories, 'patterns': patterns})

# Visão excluir categoria
def excluir_categoria(request, category_id):
   try:
        #Usuário convidado, sem permissões 
        if not check_user_permissions(request):
            return HttpResponse("Usuário sem permissão", status=403) 
        
        url = f'{FIREBASE_URL}/Categories/{category_id}/.json'
        requisicao = requests.delete(url)
        # Verifica se a requisição foi bem-sucedida (código 200)
        requisicao.raise_for_status()
   except requests.exceptions.RequestException as error:
        # Trata erros na requisição para o Firebase
        print(f"Erro na requisição para o Firebase: {error}")
        print(f"Conteúdo da resposta: {requisicao.content}")  # Adicione esta linha para imprimir o conteúdo da resposta
        return HttpResponse("Erro ao processar a requisição para o Firebase.", status=500)

    # Obtém todas as categorias cadastradas
   return redirect('list_categories')


# Visão excluir padrão
def excluir_padrao(request, pattern_id):
    try:
        #Usuário convidado, sem permissões 
        if not check_user_permissions(request):
            return HttpResponse("Usuário sem permissão", status=403) 

        url = f'{FIREBASE_URL}/Patterns/{pattern_id}/.json'
        requisicao = requests.delete(url)
        # Verifica se a requisição foi bem-sucedida (código 200)
        requisicao.raise_for_status()
    except requests.exceptions.RequestException as error:
        # Trata erros na requisição para o Firebase
        print(f"Erro na requisição para o Firebase: {error}")
        print(f"Conteúdo da resposta: {requisicao.content}")  # Adicione esta linha para imprimir o conteúdo da resposta
        return HttpResponse("Erro ao processar a requisição para o Firebase.", status=500)

    # Obtém todas as categorias cadastradas
    return redirect('list_patterns')

def process_cadPattern(request):  
    #Usuário convidado, sem permissões 
    if not check_user_permissions(request):
        return HttpResponse("Usuário sem permissão", status=403) 

    id_pattern = request.POST.get('pattern_id')
    new_description = request.POST.get('newDescricao') 
    new_category_id = request.POST.get('cbCategory')
    new_category_description = request.POST.get('cbCategory_description')
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        if id_pattern: 
            dados = {
            'description': new_description,
            'categories': {
                'id_category': new_category_id,
                'description': new_category_description  
                }
            }
            
            # Atualiza a categoria no Firebase
            requisicao = requests.put(f'{FIREBASE_URL}/Patterns/{id_pattern}.json', 
                                      data=json.dumps(dados))          

        else:
            # Dados do novo padrão(Dessa forma um novo padrão pode ter apenas uma categoria)
            dados = {
            'description': new_description,
            'categories': {
                'id_category': new_category_id,
                'description': new_category_description  
                },
            'created_by': request.session.get('user_data', {}).get('email', None),
            'registered': current_date
            }
            
            # Cria uma nova categoria no Firebase
            requisicao = requests.post(f'{FIREBASE_URL}/Patterns/.json', data=json.dumps(dados))

        # Verifica se a requisição foi bem-sucedida (código 200)
        requisicao.raise_for_status()

        # Obtém todas as categorias cadastradas
        return redirect('list_patterns')

    except requests.exceptions.RequestException as error:
        # Trata erros na requisição para o Firebase
        print(f"Erro na requisição para o Firebase: {error}")
        return HttpResponse("Erro ao processar a requisição para o Firebase.", status=500)

def get_categories():
    response = requests.get(f'{FIREBASE_URL}/Categories/.json')

    if response.status_code == 200:
        categories_data = response.json()

        # Converte os dados do Firebase em uma lista de dicionários
        categories = []
        for category_id, category_data in categories_data.items():
            category = {
                'id': category_id,
                'description': category_data.get('description', ''),
            }
            categories.append(category)

        return categories
    else:
        # Trata erros na requisição ao Firebase
        raise Exception(f"Erro ao obter dados do Firebase. Código de status: {response.status_code}")


def get_patterns():
    response = requests.get(f'{FIREBASE_URL}/Patterns/.json')

    if response.status_code == 200:
        patterns_data = response.json()

        # Converte os dados do Firebase em uma lista de dicionários
        patterns = []
        for pattern_id, patterns_data in patterns_data.items():
            pattern = {
                'id': pattern_id,
                'description': patterns_data.get('description', ''),
                'categories': patterns_data.get('categories', {}),
            }
            patterns.append(pattern)

        return patterns
    else:
        # Trata erros na requisição ao Firebase
        raise Exception(f"Erro ao obter dados do Firebase. Código de status: {response.status_code}")

def list_categories(request):
    try:
        categories = get_categories()
        return render(request, 'action/category.html', {'categories': categories})
    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)})

# Visão pra gravar os dados da categoria no banco 
def process_cadCategory(request):
    #Usuário convidado, sem permissões 
    if not check_user_permissions(request):
        return HttpResponse("Usuário sem permissão", status=403)    

    new_description = request.POST.get('newDescricao')
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    category_id = request.POST.get('category_id')   
    
    dados = {
        'description': new_description.upper(),
        'created_by': request.session.get('user_data', {}).get('email', None), 
        'registered': current_date
    }

    try:
        if category_id: 
            # Atualiza a categoria no Firebase
            requisicao = requests.put(f'{FIREBASE_URL}/Categories/{category_id}/description.json', 
                                      data=json.dumps(new_description.upper()))

        else:
            # Cria uma nova categoria no Firebase
            requisicao = requests.post(f'{FIREBASE_URL}/Categories/.json', data=json.dumps(dados))

        # Verifica se a requisição foi bem-sucedida (código 200)
        requisicao.raise_for_status()

        # Obtém todas as categorias cadastradas
        return redirect('list_categories')

    except requests.exceptions.RequestException as error:
        # Trata erros na requisição para o Firebase
        print(f"Erro na requisição para o Firebase: {error}")
        return HttpResponse("Erro ao processar a requisição para o Firebase.", status=500)
    
def check_user_permissions(request):
    """
    Verifica se o usuário tem permissões.
    Retorna True se o usuário tiver permissões, False caso contrário.
    """
    user_email = request.session.get('user_data', {}).get('email', None)
    return user_email != 'convidado@gmail.com'

