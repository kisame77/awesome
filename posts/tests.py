from django.test import TestCase, Client
from django.urls import reverse
from .models import Post, Tag
from .forms import PostCreateForm, PostEditForm
import uuid

class PostModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="Nature", slug="nature")
        self.post = Post.objects.create(
            title="Sample Post",
            artist="John Doe",
            url="https://example.com",
            image="https://example.com/image.jpg",
            body="This is a sample post",
        )
        self.post.tags.add(self.tag)


    def test_post_creation(self):
        self.assertEqual(self.post.title, "Sample Post")
        self.assertEqual(self.post.artist, "John Doe")
        self.assertEqual(self.post.url, "https://example.com")
        self.assertEqual(self.post.image, "https://example.com/image.jpg")
        self.assertEqual(self.post.body, "This is a sample post")
        self.assertIn(self.tag, self.post.tags.all())

    def test_post_str(self):
        self.assertEqual(str(self.post), "Sample Post")

    def test_tag_str(self):
        self.assertEqual(str(self.tag), "Nature")

class PostFormTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="Nature", slug="nature")

    def test_post_create_form_valid(self):
        form_data = {
            "url": "https://example.com",
            "body": "Test caption",
            "tags": [self.tag.id],
        }
        form = PostCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_create_form_invalid(self):
        form = PostCreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("url", form.errors)
        self.assertIn("body", form.errors)

    def test_post_edit_form_valid(self):
        form_data = {"body": "Updated caption", "tags": [self.tag.id]}
        form = PostEditForm(data=form_data)
        self.assertTrue(form.is_valid())

class PostViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.tag = Tag.objects.create(name="Nature", slug="nature")
        self.post = Post.objects.create(
            title="Test Post",
            artist="Jane Doe",
            url="https://example.com",
            image="https://example.com/image.jpg",
            body="Test content",
        )
        self.post.tags.add(self.tag)

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/home.html")
        self.assertIn("posts", response.context)

    def test_category_view(self):
        response = self.client.get(reverse("category", args=["nature"]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts"]), 1)

    def test_post_page_view(self):
        response = self.client.get(reverse("post", args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/post_page.html")
        self.assertEqual(uuid.UUID(response.context["post"].id), self.post.id)
        self.assertEqual(str(response.context["post"].id), str(self.post.id))



    def test_post_create_view(self):
        """Test GET request for post creation"""
        response = self.client.get(reverse("post-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/post_create.html")

        form_data = {
            "url": "https://www.flickr.com/photos/155425608@N06/34298095624/in/photolist-iLCR1X-UfNGUh-2pJK375-s3jpXo-bQvAy6-dLw199-iLBDpW-Fqhgwh-3rkQpm-iLGMjT-2fa5c85-iLwi68-5iAVcD-99jY6K-Hp3sG-2mEqCXj-b8i94v-2kToycc-vKeVkB-2jCsbK-2mk5V1r-TY4NvP-H6J28G-8FHUAW-3Zu4Av-7HwuEi-iLBezF-2pPcAQH-2pEERcm-iLHoVx-2i7sJdG-HoR4u-Q6oGjx-2mju2Gz-2i7vm33-LGvDsH-8UGJSB-243kAf6-dbKEZo-2kfX4vu-cALPFo-2i7vkPY-2ivMfys-Daemmm-2iUsma2-EfJroS-STVNS8-GdAL7y-G4hmWQ-GJBtKC/",  # Make sure this URL is valid
            "body": "New Caption",
            "tags": [self.tag.id],  # Ensure tag exists in the test setup
        }   
        
        response = self.client.post(reverse("post-create"), data=form_data)
        
        # Debugging: Print errors if form submission fails
        if response.status_code == 200:
            print("Form errors:", response.context.get("form").errors)
        
        self.assertEqual(response.status_code, 302)  # Expecting a redirect to home

    def test_post_edit_view(self):
        response = self.client.get(reverse("post-edit", args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/post_edit.html")

        form_data = {"body": "Updated Caption", "tags": [self.tag.id]}
        response = self.client.post(reverse("post-edit", args=[self.post.id]), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects to home
        self.post.refresh_from_db()
        self.assertEqual(self.post.body, "Updated Caption")

    def test_post_delete_view(self):
        """Test the delete view for a post"""
        
        # Step 1: Ensure the post exists before deletion
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())

        # Step 2: Test GET request - should return the delete confirmation page
        response = self.client.get(reverse("post-delete", args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "posts/post_delete.html")

        # Step 3: Test POST request - actually delete the post
        response = self.client.post(reverse("post-delete", args=[self.post.id]))
        self.assertEqual(response.status_code, 302)  # Expecting a redirect (typically to home)

        # Step 4: Ensure the post no longer exists
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
