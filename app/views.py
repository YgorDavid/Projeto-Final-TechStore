from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm 
from django.contrib import messages
from django import forms
from .models import Perfil 

# --- 1. FORMULÁRIO DE CADASTRO INTELIGENTE (HÍBRIDO PF/PJ) ---
class CadastroForm(UserCreationForm):
    documento = forms.CharField(
        label="CPF ou CNPJ",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '000.000.000-00 ou 00.000.000/0000-00',
        })
    )
    cep = forms.CharField(
        label="CEP",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'})
    )

    field_order = ['username', 'documento', 'cep', 'password', 'password_confirm']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None
            field.widget.attrs.update({'class': 'form-control'})

    def clean_documento(self):
        doc = ''.join(filter(str.isdigit, self.cleaned_data.get('documento', '')))
        if len(doc) not in [11, 14]:
            raise forms.ValidationError("Digite um CPF (11 números) ou CNPJ (14 números) válido.")
        return doc

# --- 2. VIEWS (LÓGICA DAS PÁGINAS) ---

def home_view(request):
    context = {'nome_empresa': 'TechStore'}
    return render(request, 'home.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            usuario = authenticate(username=username, password=password)
            if usuario is not None:
                login(request, usuario)
                return redirect('home')
            else:
                messages.error(request, "Usuário ou senha inválidos.")
        else:
            messages.error(request, "Informações inválidas.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            doc = form.clean_documento()
            tipo = 'PF' if len(doc) == 11 else 'PJ'
            
            Perfil.objects.create(
                usuario=user,
                tipo_pessoa=tipo,
                documento=doc,
                cep=form.cleaned_data.get('cep')
            )
            
            messages.success(request, f"Bem-vindo à TechStore! Conta {tipo} criada com sucesso.")
            return redirect('login')
    else:
        form = CadastroForm()
    return render(request, 'cadastro.html', {'form': form})
    
def logout_view(request):
    logout(request)
    return redirect('login')