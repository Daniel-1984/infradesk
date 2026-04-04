from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Department(models.Model):
    name = models.CharField('Nome', max_length=100)
    code = models.CharField('Código', max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('technician', 'Técnico'),
        ('user', 'Usuário'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Departamento'
    )
    role = models.CharField('Perfil', max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField('Telefone', max_length=20, blank=True)
    employee_id = models.CharField('Matrícula', max_length=30, blank=True)

    bio = models.TextField('Observações', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} — {self.get_role_display()}'

    def is_admin(self):
        return self.role == 'admin'

    def is_technician(self):
        return self.role in ('admin', 'technician')

    def get_avatar_url(self):
        return None


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
