# -*- coding: UTF-8 -*-
import re
from django import forms
from django.contrib.auth.models import User


mensajes = {
    'invalid': 'El valor ingresado es incorrecto',
    'required': 'Este campo no puede ser vacio'
}

class RegistracionForm(forms.Form):
    username = forms.CharField(
        label = "Nombre de usuario",
        max_length = 30,
        required = True,
        error_messages=mensajes,
        widget = forms.TextInput()
    )
    email = forms.EmailField(
        label = "Email",
        required = True,
        error_messages=mensajes,
        widget=forms.TextInput()
    )
    mensajes['min_length'] = 'La contraseña debe tener al menos 8 caracteres.'
    password1 = forms.CharField(
        label = "Contraseña",
        required = True,
        min_length = 8,
        error_messages=mensajes,
        widget = forms.PasswordInput(render_value=False)
    )
    password2 = forms.CharField(
        label = "Repetir contraseña",
        required = True,
        min_length = 8,
        error_messages=mensajes,
        widget = forms.PasswordInput(render_value=False)
    )
    confirmation_key = forms.CharField(
        max_length = 40,
        required = False,
        widget = forms.HiddenInput()
    )

    def clean_username(self):
        if not re.compile(r"^\w+$").search(self.cleaned_data["username"]):
            raise forms.ValidationError("El nombre de usuario solo puede contener letras, numeros y/o guion bajo.")
        try:
            User.objects.get(username__iexact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError("El nombre de usuario ya esta utilizado. Por favor elegi otro.")

    def clean_email(self):
        value = self.cleaned_data["email"]
        try:
            User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            return value
        raise forms.ValidationError("Ya hay una cuenta creada con este Email.")
        return value

    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError("Las contraseñas deben ser iguales.")
        return self.cleaned_data

    def create_user(self, username=None, commit=True):
        user = User()
        if username is None:
            raise NotImplementedError("SignupForm.create_user does not handle "
                "username=None case. You must override this method.")
        user.username = username
        user.email = self.cleaned_data["email"].strip().lower()
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user

    def login(self, request, user):
        # nasty hack to get get_user to work in Django
        user.backend = "django.contrib.auth.backends.ModelBackend"
        perform_login(request, user)

    def save(self, request=None):
        # don't assume a username is available. it is a common removal if
        # site developer wants to use email authentication.
        username = self.cleaned_data.get("username")
        email = self.cleaned_data["email"]

        if self.cleaned_data["confirmation_key"]:
            from friends.models import JoinInvitation # @@@ temporary fix for issue 93
            try:
                join_invitation = JoinInvitation.objects.get(confirmation_key=self.cleaned_data["confirmation_key"])
                confirmed = True
            except JoinInvitation.DoesNotExist:
                confirmed = False
        else:
            confirmed = False

        # @@@ clean up some of the repetition below -- DRY!

        if confirmed:
            if email == join_invitation.contact.email:
                new_user = self.create_user(username)
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if request:
                    messages.add_message(request, messages.INFO,
                        ugettext(u"Your email address has already been verified")
                    )
                # already verified so can just create
                EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
            else:
                new_user = self.create_user(username)
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if email:
                    if request:
                        messages.add_message(request, messages.INFO,
                            ugettext(u"Confirmation email sent to %(email)s") % {
                                "email": email,
                            }
                        )
                    EmailAddress.objects.add_email(new_user, email)
        else:
            new_user = self.create_user(username)
            if email:
                if request and not EMAIL_VERIFICATION:
                    messages.add_message(request, messages.INFO,
                        ugettext(u"Confirmation email sent to %(email)s") % {
                            "email": email,
                        }
                    )
                EmailAddress.objects.add_email(new_user, email)

        if EMAIL_VERIFICATION:
            new_user.is_active = False
            new_user.save()

        self.after_signup(new_user)

        return new_user
