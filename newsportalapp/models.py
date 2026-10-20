
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Province(models.TextChoices):
    KOSHI = "koshi", "Koshi"
    MADHESH = "madhesh", "Madhesh"
    BAGMATI = "bagmati", "Bagmati"
    GANDAKI = "gandaki", "Gandaki"
    LUMBINI = "lumbini", "Lumbini"
    KARNALI = "karnali", "Karnali"
    SUDURPASHCHIM = "sudurpashchim", "Sudurpashchim"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    class Role(models.TextChoices):
        CO_ADMIN = "co_admin", "Co Admin"
        AUTHOR = "author", "Author"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.AUTHOR
    )

    province = models.CharField(
        max_length=20,
        choices=Province.choices,
        blank=True
    )

    allowed_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="assigned_users"
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending Review"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    summary = models.CharField(max_length=400, blank=True)
    content = models.TextField()

    province = models.CharField(
        max_length=20,
        choices=Province.choices
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="articles"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="articles"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "article"
            slug = base_slug
            number = 2

            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{number}"
                number += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
