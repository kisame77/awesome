import pytest
import uuid
from django.urls import reverse
from django.test import Client
from .models import Post, Tag
from .forms import PostCreateForm, PostEditForm

@pytest.fixture
def client():
    """Fixture to provide Django's test client."""
    return Client()

@pytest.fixture
def tag(db):
    """Fixture to create a tag."""
    return Tag.objects.create(name="Nature", slug="nature")

@pytest.fixture
def post(db):
    """Fixture to create a post."""
    post = Post.objects.create(
        title="Sample Post",
        artist="John Doe",
        url="https://example.com",
        image="https://example.com/image.jpg",
        body="This is a sample post",
    )
    return post

@pytest.fixture
def post_with_tag(db, tag):
    """Fixture to create a post with a tag."""
    post = Post.objects.create(
        title="Test Post",
        artist="Jane Doe",
        url="https://example.com",
        image="https://example.com/image.jpg",
        body="Test content",
    )
    post.tags.add(tag)
    return post

# Model Tests
def test_post_creation(post, tag):
    """Test post creation"""
    post.tags.add(tag)
    assert post.title == "Sample Post"
    assert post.artist == "John Doe"
    assert post.url == "https://example.com"
    assert post.image == "https://example.com/image.jpg"
    assert post.body == "This is a sample post"
    assert tag in post.tags.all()

def test_post_str(post):
    """Test post string representation"""
    assert str(post) == "Sample Post"

def test_tag_str(tag):
    """Test tag string representation"""
    assert str(tag) == "Nature"

# Form Tests
def test_post_create_form_valid(tag):
    """Test valid post creation form"""
    form_data = {
        "url": "https://example.com",
        "body": "Test caption",
        "tags": [tag.id],
    }
    form = PostCreateForm(data=form_data)
    assert form.is_valid()

def test_post_create_form_invalid():
    """Test invalid post creation form"""
    form = PostCreateForm(data={})
    assert not form.is_valid()
    assert "url" in form.errors
    assert "body" in form.errors

def test_post_edit_form_valid(tag):
    """Test valid post edit form"""
    form_data = {"body": "Updated caption", "tags": [tag.id]}
    form = PostEditForm(data=form_data)
    assert form.is_valid()

# View Tests
def test_home_view(client, db):
    """Test home page view"""
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert "posts" in response.context
    assert "posts/home.html" in [t.name for t in response.templates]

def test_category_view(client, post_with_tag):
    """Test category view"""
    response = client.get(reverse("category", args=["nature"]))
    assert response.status_code == 200
    assert len(response.context["posts"]) == 1

def test_post_page_view(client, post_with_tag):
    """Test single post page view"""
    response = client.get(reverse("post", args=[post_with_tag.id]))
    assert response.status_code == 200
    assert "posts/post_page.html" in [t.name for t in response.templates]
    assert uuid.UUID(str(response.context["post"].id)) == post_with_tag.id
    assert str(response.context["post"].id) == str(post_with_tag.id)

def test_post_create_view(client, tag):
    """Test post create view"""
    response = client.get(reverse("post-create"))
    assert response.status_code == 200
    assert "posts/post_create.html" in [t.name for t in response.templates]

    form_data = {
        "url": "https://www.flickr.com/photos/sample",
        "body": "New Caption",
        "tags": [tag.id],
    }
    response = client.post(reverse("post-create"), data=form_data)

    # Debugging: Print errors if form submission fails
    if response.status_code == 200:
        print("Form errors:", response.context.get("form").errors)

    assert response.status_code == 302  # Expecting a redirect

def test_post_edit_view(client, post_with_tag, tag):
    """Test post edit view"""
    response = client.get(reverse("post-edit", args=[post_with_tag.id]))
    assert response.status_code == 200
    assert "posts/post_edit.html" in [t.name for t in response.templates]

    form_data = {"body": "Updated Caption", "tags": [tag.id]}
    response = client.post(reverse("post-edit", args=[post_with_tag.id]), data=form_data)

    assert response.status_code == 302  # Expecting a redirect
    post_with_tag.refresh_from_db()
    assert post_with_tag.body == "Updated Caption"

def test_post_delete_view(client, post_with_tag):
    """Test the delete view for a post"""
    
    # Ensure the post exists before deletion
    assert Post.objects.filter(id=post_with_tag.id).exists()

    # Test GET request - should return the delete confirmation page
    response = client.get(reverse("post-delete", args=[post_with_tag.id]))
    assert response.status_code == 200
    assert "posts/post_delete.html" in [t.name for t in response.templates]

    # Test POST request - actually delete the post
    response = client.post(reverse("post-delete", args=[post_with_tag.id]))
    assert response.status_code == 302  # Expecting a redirect

    # Ensure the post no longer exists
    assert not Post.objects.filter(id=post_with_tag.id).exists()
