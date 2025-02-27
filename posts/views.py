from django.shortcuts import redirect, render

from .forms import PostCreateForm
from .models import Post


def home_view(request):
    posts = Post.objects.all()
    context = {"posts": posts}
    return render(request, "posts/home.html", context)


def post_create_view(request):
    form = PostCreateForm()

    if request.method == "POST":
        form = PostCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")

    context = {"form": form}
    return render(request, "posts/post_create.html", context)
