from django.forms import (
    Form, CharField, Textarea, PasswordInput, ChoiceField, DateField,
    ImageField, EmailField,
)

from fb.models import UserProfile


class UserPostForm(Form):
    text = CharField(widget=Textarea(
        attrs={'rows': 1, 'cols': 40, 'class': 'form-control','placeholder': "What's on your mind?"}))


class UserPostCommentForm(Form):
    text = CharField(widget=Textarea(
        attrs={'rows': 1, 'cols': 50, 'class': 'form-control','placeholder': "Write a comment..."}))


class UserLogin(Form):
    username = CharField(max_length=30)
    password = CharField(widget=PasswordInput)

class UserSignUp(Form):
    first_name = CharField(max_length=100)
    last_name = CharField(max_length=100)
    gender = ChoiceField(choices=UserProfile.GENDERS)
    date_of_birth = DateField( required=False)
    username = CharField(max_length=30)
    password = CharField(widget=PasswordInput)
    confirm_password = CharField(widget=PasswordInput)
   # email = EmailField()
    email = CharField(max_length=30)
    avatar = ImageField()



class UserProfileForm(Form):
    first_name = CharField(max_length=100, required=False)
    last_name = CharField(max_length=100, required=False)
    gender = ChoiceField(choices=UserProfile.GENDERS, required=False)
    date_of_birth = DateField(required=False)
    avatar = ImageField(required=False)
