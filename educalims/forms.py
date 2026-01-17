from django import forms
from django.contrib.auth.models import User


class CustomUserCreationForm(forms.Form):
    """Formulaire d'inscription personnalisé avec validation souple"""

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre@email.com'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })
    )

    RECOMMANDATION_CHOICES = [
        ('', '---------'),
        ('gosenmarket', 'Gosenmarket'),
        ('A01', 'A01'),
        ('A02', 'A02'),
        ('A03', 'A03'),
        ('A04', 'A04'),
        ('A05', 'A05'),
        ('aucun', 'Aucun'),
    ]

    recommande_par = forms.ChoiceField(
        choices=RECOMMANDATION_CHOICES,
        required=True,
        initial='aucun',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Recommandé par'
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ce nom d\'utilisateur est déjà pris.')
        if len(username) < 3:
            raise forms.ValidationError('Le nom d\'utilisateur doit contenir au moins 3 caractères.')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 4:
            raise forms.ValidationError('Le mot de passe doit contenir au moins 4 caractères.')
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')

        return cleaned_data


class LoginForm(forms.Form):
    """Formulaire de connexion personnalisé"""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
    )
