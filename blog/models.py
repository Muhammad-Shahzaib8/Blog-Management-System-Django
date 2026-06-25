from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Blog(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    short_description = models.CharField(max_length=300)
    content = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)

    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)

    meta_title = models.CharField(max_length=250, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.short_description
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, default="Anonymous")
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment[:50]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    def __str__(self):
        return self.user.username


class Rating(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='ratings')
    name = models.CharField(max_length=100, default="Anonymous")
    rating = models.PositiveIntegerField(default=5)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blog.title} - {self.rating} Stars"
class BlogLike(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'user')

    def __str__(self):
        return f"{self.user.username} liked {self.blog.title}"
    class BlogLike(models.Model):

        blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name='blog_likes'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('blog', 'user')

    def __str__(self):
        return f"{self.user.username} liked {self.blog.title}"