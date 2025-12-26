from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser, PermissionsMixin


class User(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # required by AbstractUser
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.email


class HOAGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner_email = models.EmailField(unique=True)
    users = models.ManyToManyField(User, through='HOAMembership', related_name='hoa_groups')

    class Meta:
        db_table = 'hoa_groups'

    def __str__(self):
        return self.name

    def is_admin(self, user):
        """Check if a user is an admin of this HOA group"""
        return self.memberships.filter(user=user, role='admin').exists()

    def get_user_role(self, user):
        """Get the role of a user in this HOA group"""
        membership = self.memberships.filter(user=user).first()
        return membership.role if membership else None


class HOAMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hoa_memberships')
    hoa_group = models.ForeignKey(HOAGroup, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hoa_memberships'
        unique_together = ['user', 'hoa_group']

    def __str__(self):
        return f"{self.user.email} - {self.hoa_group.name} ({self.role})"


class House(models.Model):
    address = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(User, related_name='houses')

    class Meta:
        db_table = 'houses'

    def __str__(self):
        return self.address


class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    hoa_group = models.ForeignKey(HOAGroup, on_delete=models.CASCADE, related_name='documents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'

    def __str__(self):
        return self.title
