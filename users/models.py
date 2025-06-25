from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
    Group,
    Permission,
)
from django.db import models
from ecommerce.utils.models import UUID, TimeStampModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role="buyer", **extra_fields):
        if not email:
            raise ValueError("Email is required for creating the user Profile")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, role="superadmin", **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, UUID, TimeStampModel):
    role_choices = (
        ("buyer", "Buyer"),
        ("seller", "Seller"),
        ("admin", "Admin"),
        ("superadmin", "Superadmin"),
    )

    fullname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=role_choices, default="buyer")
    phoneNo = models.CharField(max_length=10, blank=True, null=True)
    profilePic = models.URLField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return f"{self.email}, ({self.role})"
