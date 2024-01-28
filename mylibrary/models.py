from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, is_admin=False, name='', **extra_fields):
        if not username:
            raise ValueError('Username must not be empty.')

        extra_fields.setdefault('is_staff', is_admin)
        extra_fields.setdefault('is_superuser', is_admin)

        user = self.model(username=username, name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, name='', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, is_admin=True, name=name, **extra_fields)

class User(AbstractUser):
    USERNAME_FIELD = 'username'
    is_admin = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    objects = CustomUserManager()

class Book(models.Model):
    title = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, unique=True)
    author = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.book.title}'
