from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

# Mudamos o nome para CadastroForm para bater com o que está na sua views.py
class CadastroForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    tipo_pessoa = forms.ChoiceField(
        choices=[('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_pessoa'})
    )
    cpf_cnpj = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_cpf_cnpj'}))
    telefone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_telefone'}))
    cep = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_cep'}))
    logradouro = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_logradouro'}))
    numero = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    bairro = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_bairro'}))
    cidade = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_cidade', 'readonly': 'readonly'}))
    estado = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_estado', 'readonly': 'readonly'}))

    class Meta:
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True 
        
        if commit:
            user.save()
            Perfil.objects.create(
                user=user,
                tipo_pessoa=self.cleaned_data['tipo_pessoa'],
                cpf_cnpj=self.cleaned_data['cpf_cnpj'],
                telefone=self.cleaned_data['telefone'],
                cep=self.cleaned_data['cep'],
                logradouro=self.cleaned_data['logradouro'],
                numero=self.cleaned_data['numero'],
                bairro=self.cleaned_data['bairro'],
                cidade=self.cleaned_data['cidade'],
                estado=self.cleaned_data['estado'],
            )
        return user

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']
        widgets = {
            'nota': forms.Select(attrs={'class': 'form-select'}),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Conte sua experiência com o produto...'
            }),
        }
        labels = {
            'nota': 'Sua avaliação',
            'comentario': 'Comentário (opcional)',
        }

#  Pode ser usado para criar um formulário de cadastro de produtos no futuro.

# class CursoForm(forms.ModelForm):
#     class Meta:
#         model = Curso
#         fields = [
#             'nome',
#             'carga_horaria',
#             'nivel',
#  ]