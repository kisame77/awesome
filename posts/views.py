from django.shortcuts import redirect, render, get_object_or_404
import requests
from bs4 import BeautifulSoup
from .forms import PostCreateForm, PostEditForm
from .models import Post, Tag
from django.contrib import messages
from requests.exceptions import RequestException


def home_view(request, tag=None):
    if tag:
        posts = Post.objects.filter(tags__slug=tag)
        tag = get_object_or_404(Tag, slug=tag)
    else:
        posts = Post.objects.all()
    categories = Tag.objects.all()
    context = {"posts": posts, "categories": categories, "tag": tag}
    return render(request, "posts/home.html", context)


# def post_create_view(request):
#     form = PostCreateForm()

#     if request.method == "POST":
#         form = PostCreateForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)

#             website = requests.get(form.data["url"])

#             sourcecode = BeautifulSoup(website.text, "html.parser")

#             find_image = sourcecode.select(
#                 'meta[content^="https://live.staticflickr.com/"]'
#             )
#             print("ffff",find_image)
#             image = find_image[0]["content"]
#             post.image = image

#             find_title = sourcecode.select("h1.photo-title")
#             title = find_title[0].text.strip()
#             post.title = title

#             find_artist = sourcecode.select("a.owner-name")
#             artist = find_artist[0].text.strip()
#             post.artist = artist

#             post.save()
#             form.save_m2m()
#             return redirect("home")

#     context = {"form": form}
#     return render(request, "posts/post_create.html", context)


def post_create_view(request):
    form = PostCreateForm()

    if request.method == "POST":
        form = PostCreateForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            url = form.cleaned_data.get("url")  # Get cleaned user input

            try:
                website = requests.get(
                    url, timeout=5
                )  # Set timeout to prevent slow requests
                website.raise_for_status()  # Raise error for bad responses (e.g., 404, 500)

                sourcecode = BeautifulSoup(website.text, "html.parser")

                # Extract image
                find_image = sourcecode.select(
                    'meta[content^="https://live.staticflickr.com/"]'
                )
                if not find_image:
                    messages.error(request, "No valid image found on the page.")
                    return render(request, "posts/post_create.html", {"form": form})

                post.image = find_image[0]["content"]

                # Extract title
                find_title = sourcecode.select("h1.photo-title")
                post.title = find_title[0].text.strip() if find_title else "Untitled"

                # Extract artist
                find_artist = sourcecode.select("a.owner-name")
                post.artist = find_artist[0].text.strip() if find_artist else "Unknown"

                post.save()
                form.save_m2m()

                messages.success(request, "Post created successfully!")
                return redirect("home")

            except RequestException as e:  # Handles network issues, 404 errors, etc.
                messages.error(request, f"Error fetching data: {str(e)}")
            except IndexError:  # Handles missing elements on the page
                messages.error(request, "Error extracting data from the URL.")
            except Exception as e:  # Catch any other unexpected errors
                messages.error(request, f"An unexpected error occurred: {str(e)}")

        else:
            messages.error(
                request, "Invalid form submission. Please correct the errors."
            )

    return render(request, "posts/post_create.html", {"form": form})


def post_delete_view(request, pk):
    post = get_object_or_404(Post, id=pk)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted")
        return redirect("home")

    context = {"post": post}
    return render(request, "posts/post_delete.html", context)


def post_edit_view(request, pk):
    post = get_object_or_404(Post, id=pk)

    form = PostEditForm(instance=post)

    if request.method == "POST":
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid:
            form.save()
            messages.success(request, "Post updated")
            return redirect("home")

    context = {"post": post, "form": form}
    return render(request, "posts/post_edit.html", context)


def post_page_view(request, pk):
    # post = Post.objects.all(id=pk)
    post = get_object_or_404(Post, id=pk)
    context = {"post": post}
    return render(request, "posts/post_page.html", context)
