from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .models import ContactMessage


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save(commit=False)
            
            if request.user.is_authenticated:
                contact_message.nom = request.user.get_full_name() or request.user.username
                contact_message.email = request.user.email
            
            contact_message.save()
            
            messages.success(
                request,
                'Votre message a été envoyé avec succès! Nous vous répondrons dans les plus brefs délais.'
            )
            return redirect('contact')
    else:
        form = ContactForm()
    
    if request.user.is_authenticated:
        form.fields['nom'].initial = request.user.get_full_name() or request.user.username
        form.fields['email'].initial = request.user.email
    
    return render(request, 'gosen/contact.html', {'form': form})
