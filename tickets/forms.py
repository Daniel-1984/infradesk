from django import forms
from django.contrib.auth.models import User
from .models import Ticket, TicketComment


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority', 'asset', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva brevemente o problema'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descreva detalhadamente o problema, passos para reproduzir, impacto...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'title': 'Título do Chamado',
            'description': 'Descrição',
            'category': 'Categoria',
            'priority': 'Prioridade',
            'asset': 'Equipamento Relacionado',
            'due_date': 'Prazo',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['asset'].empty_label = '— Nenhum equipamento —'
        self.fields['asset'].required = False

        if user and not (hasattr(user, 'profile') and user.profile.is_technician()):
            self.fields.pop('priority', None)


class TicketAdminForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority', 'status', 'assigned_to', 'asset', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'title': 'Título',
            'description': 'Descrição',
            'category': 'Categoria',
            'priority': 'Prioridade',
            'status': 'Status',
            'assigned_to': 'Atribuído a',
            'asset': 'Equipamento',
            'due_date': 'Prazo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        technicians = User.objects.filter(
            profile__role__in=['admin', 'technician']
        ).order_by('first_name')
        self.fields['assigned_to'].queryset = technicians
        self.fields['assigned_to'].empty_label = '— Não atribuído —'
        self.fields['assigned_to'].required = False
        self.fields['asset'].empty_label = '— Nenhum equipamento —'
        self.fields['asset'].required = False


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escreva sua resposta ou atualização...'
            }),
        }
        labels = {
            'content': 'Comentário',
            'is_internal': 'Nota interna (visível apenas para técnicos)',
        }


class TicketFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'Todos os Status')] + Ticket.STATUS_CHOICES
    PRIORITY_CHOICES = [('', 'Todas as Prioridades')] + Ticket.PRIORITY_CHOICES
    CATEGORY_CHOICES = [('', 'Todas as Categorias')] + Ticket.CATEGORY_CHOICES

    status = forms.ChoiceField(
        choices=STATUS_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Buscar chamado...'
        })
    )
