from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # O usuário já começa inativo
        user.is_active = False
        if commit:
            user.save()
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