from django import forms
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import datetime
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, Feedback

class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'phone']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

class ReservationForm(forms.Form):
    # Имя: только буквы и пробелы, минимум 2 символа
    name = forms.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex='^[a-zA-Zа-яА-ЯёЁ\s]+$',
                message='Имя может содержать только буквы и пробелы.'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваше имя*',
            'class': 'form-control'
        }),
        label='Имя',
        required=True
    )

    # Email: стандартная валидация + проверка домена
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ваш Email*',
            'class': 'form-control'
        }),
        label='Email',
        required=True
    )

    # Телефон: только цифры, +, -, пробелы
    phone = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex='^\+?[0-9\s\-]+$',
                message='Номер телефона должен содержать только цифры, "+" или "-".'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваш номер телефона*',
            'class': 'form-control'
        }),
        label='Телефон',
        required=True
    )

    # Количество гостей: от 1 до 12
    guests = forms.IntegerField(
        validators=[
            MinValueValidator(1, 'Минимум 1 гость.'),
            MaxValueValidator(12, 'Максимум 12 гостей.')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'number-guests'
        }, choices=[
            (1, '1'), (2, '2'), (3, '3'), (4, '4'),
            (5, '5'), (6, '6'), (7, '7'), (8, '8'),
            (9, '9'), (10, '10'), (11, '11'), (12, '12')
        ]),
        label='Гости',
        required=True
    )

    # Дата: не раньше сегодняшнего дня
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'placeholder': 'dd/mm/yyyy',
            'class': 'form-control',
            'type': 'date'
        }),
        validators=[
            RegexValidator(
                regex='^\d{2}/\d{2}/\d{4}$',
                message='Введите дату в формате ДД/ММ/ГГГГ.'
            )
        ],
        label='Дата',
        required=True
    )

    # Время: выбор из списка
    time = forms.ChoiceField(
        choices=[
            ('Breakfast', 'Завтрак (8:00–11:00)'),
            ('Lunch', 'Обед (12:00–15:00)'),
            ('Dinner', 'Ужин (18:00–22:00)')
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'time'
        }),
        label='Время',
        required=True
    )

    # Комментарий: необязательное поле
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Комментарии и пожелания',
            'class': 'form-control',
            'rows': 3
        }),
        label='Комментарий',
        required=False,
        max_length=500
    )

    # Дополнительная валидация даты (проверка, что не в прошлом)
    def clean_date(self):
        date = self.cleaned_data['date']
        if date < datetime.date.today():
            raise forms.ValidationError('Дата не может быть в прошлом!')
        return date


