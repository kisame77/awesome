from django.shortcuts import render


def home_view(request):
    title = "Welcome to Django"
    context = {"title": title}
    return render(request, "posts/home.html", context)
