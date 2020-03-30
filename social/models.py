from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

# Create your models here.

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')

class Post(models.Model):
    objects = models.Manager() # Our default manager
    published = PublishedManager() # Our custom model manager which filter only published post

    STATUS_CHOICES = (
        ('draft','Draft'),
        ('published','Published'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES, default='draft')
    restrict_comment = models.BooleanField(default=False)
    favourite = models.ManyToManyField(User, related_name='favourite', blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title
    
    def total_likes(self):
        return self.likes.count()
    
    def get_absolute_url(self):
        return reverse("_social:post_detail", args=[self.id, self.slug])
    
@receiver(pre_save, sender=Post) 
def pre_save_slug(sender, **kwargs):
    slug = slugify(kwargs['instance'].title)
    kwargs['instance'].slug = slug

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    dob = models.DateField(null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)


    def __str__(self):
        return "Profile of user {}".format(self.user)


class Images(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.post.title + ' Image'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.ForeignKey('Comment', null=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title}, {self.user.username}"
    
    
    