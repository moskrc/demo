# coding: utf-8
from django.db import models
from django.conf import settings
from django.utils import six, timezone
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.contrib.auth.hashers import (
    check_password
)



User = settings.AUTH_USER_MODEL


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    type = models.IntegerField(default=0)
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    token = models.CharField(max_length=32)
    owner = models.IntegerField(blank=True, null=True)
    suspended = models.IntegerField(blank=True, null=True)
    validated = models.IntegerField(default=0)
    added_date = models.IntegerField(blank=True, null=True)
    timezone = models.CharField(max_length=32)
    last_ip = models.CharField(max_length=32)
    country = models.CharField(max_length=32)
    mobile = models.IntegerField(blank=True, null=True)

    first_name = models.CharField('First name', max_length=30, blank=True)
    last_name = models.CharField('Last name', max_length=30, blank=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def is_staff(self):
        return self.is_superuser

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, 'plain$1$%s' % self.password, setter)


    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'
