from django.shortcuts import redirect, render
import requests
from bs4 import BeautifulSoup
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
            post = form.save(commit=False)

            website = requests.get(form.data['url'])

            sourcecode = BeautifulSoup(website.text, 'html.parser')

            find_image = sourcecode.select('meta[content^="https://live.staticflickr.com/"]')
            image = find_image[0]['content']
            post.image = image

            find_title = sourcecode.select('h1.photo-title')
            title = find_title[0].text.strip()
            post.title = title

            find_artist = sourcecode.select('a.owner-name')
            artist = find_artist[0].text.strip()
            post.artist = artist

            post.save()
            return redirect("home")

    context = {"form": form}
    return render(request, "posts/post_create.html", context)
