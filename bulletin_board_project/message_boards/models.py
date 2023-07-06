from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/boards/')
    title = models.CharField(max_length=255)
    text = RichTextUploadingField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def preview(self):
        return self.text[:124] + '...'

    def __str__(self):
        return self.title


class Response(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.text[:124]


class EmailKey(models.Model):
    key = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sended_at = models.DateTimeField(auto_now_add=True)