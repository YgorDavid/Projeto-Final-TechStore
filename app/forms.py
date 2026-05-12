from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Mudamos o nome para CadastroForm para bater com o que está na sua views.py
class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")
    
    tipo_pessoa = forms.ChoiceField(
        choices=[('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')],
        label="Tipo de Cadastro",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_pessoa'})
    )
    
    cpf_cnpj = forms.CharField(
        max_length=18, 
        label="CPF ou CNPJ",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_cpf_cnpj'})
    )
    
    cep = forms.CharField(
        max_length=9, 
        label="CEP",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_cep'})
    )

    telefone = forms.CharField(
        label="Celular / WhatsApp", 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'})
    )
    
    endereco = forms.CharField(
        max_length=255, 
        label="Endereço Completo",
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_endereco', 'readonly': 'readonly'})
    )

    class Meta:
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False 
        
        if commit:
            user.save()
            # Cria o perfil vinculado ao usuário recém-criado
            Perfil.objects.create(
                user=user,
                tipo_pessoa=self.cleaned_data['tipo_pessoa'],
                cpf_cnpj=self.cleaned_data['cpf_cnpj'],
                cep=self.cleaned_data['cep'],
                telefone=self.cleaned_data['telefone'],
                endereco=self.cleaned_data['endereco']
            )
        return user

  
#  Pode ser usado para criar um formulário de cadastro de produtos no futuro.

# class CursoForm(forms.ModelForm):
#     class Meta:
#         model = Curso
#         fields = [
#             'nome',
#             'carga_horaria',
#             'nivel',
#  ]

# Pode ser usado para criar um formulário de avaliação de produtos no futuro.

# class AvaliacaoForm(forms.ModelForm):
#     class Meta:
#         model = Avaliacao
#         fields = [
#             'nome_aluno',
#             'nome_curso',
#             'nota',
#             'comentario',
#  ]