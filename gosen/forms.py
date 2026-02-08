from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Formulaire d'inscription étendu"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre@email.com'
        })
    )
    telephone = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+241 XX XX XX XX'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'telephone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom d\'utilisateur'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Créer le profil utilisateur s'il n'existe pas
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'telephone': self.cleaned_data.get('telephone', '')}
            )
        return user


class UserProfileForm(forms.ModelForm):
    """Formulaire de profil utilisateur"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ('telephone', 'device_id')
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'device_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.username = self.cleaned_data['username']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
                profile.save()
        return profile


class SubscriptionForm(forms.Form):
    """Formulaire de souscription à un abonnement"""
    TYPE_ABONNEMENT_CHOICES = [
        ('mensuel', 'Mensuel - 5000 XAF/mois'),
        ('annuel', 'Annuel - 50000 XAF/an (économie de 2 mois)'),
        ('a_vie', 'À vie - 150000 XAF (accès illimité)'),
    ]

    type_abonnement = forms.ChoiceField(
        choices=TYPE_ABONNEMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'subscription-choice'})
    )
    telephone = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numéro pour le paiement (Moov Money/Airtel)'
        })
    )
    accepter_conditions = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
