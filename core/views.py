from django.shortcuts import render, redirect
from django.contrib.auth import logout

from item.models import Category, Item


def index(request):
    items = Item.objects.all()[0:6]
    categories = Category.objects.all()

    return render(request, 'core/index.html', {
        'categories': categories,
        'items': items,
    })


def contact(request):
    return render(request, 'core/contact.html')


def logout_view(request):
    logout(request)
    return redirect('/')
