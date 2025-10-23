from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        print(f"User {user} создан.")
        try:
            basic_group = Group.objects.get(name='common')
            print(f"Добавляю пользователя {user} в группу 'common'.")
            basic_group.user_set.add(user)
            print("Добавление прошло успешно.")
        except Exception as e:
            print(f"Ошибка при добавлении в группу: {e}")
        return user

class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "Имя")
    last_name = forms.CharField(label = "Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", )