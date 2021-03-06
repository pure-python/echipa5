from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from fb.models import UserPost, UserPostComment, UserProfile
from fb.forms import (
    UserPostForm, UserPostCommentForm, 
    UserLogin, UserProfileForm, UserSignUp,
)
import datetime

@login_required
def index(request):
    if request.method == 'GET':
        form = UserPostForm()
    elif request.method == 'POST':
        form = UserPostForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            post = UserPost(text=text, author=request.user)
            post.save()
    posts = UserPost.objects.filter(author__profile__in=request.user.profile.friends.all())
    profiles = request.user.profile.friends.filter(date_of_birth__gt=datetime.datetime.now)

    context = {
        'profiles': profiles,
        'posts': posts,
        'form': form,
    }
    return render(request, 'index.html', context)


@login_required
def post_details(request, pk):
    post = UserPost.objects.get(pk=pk)

    if request.method == 'GET':
        form = UserPostCommentForm()
    elif request.method == 'POST':
        form = UserPostCommentForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            comment = UserPostComment(text=cleaned_data['text'],
                                      post=post,
                                      author=request.user)
            comment.save()

    comments = UserPostComment.objects.filter(post=post)

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }

    return render(request, 'post_details.html', context)


def signup_view(request):
    if request.method == 'GET':
        signup_form = UserSignUp()
        context = {
            'form': signup_form,
        }
        return render(request, 'signup.html', context)
    if request.method == 'POST':
        form = UserSignUp(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            gender = form.cleaned_data['gender']
            date_of_birth = form.cleaned_data['date_of_birth']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            password_doublecheck = form.cleaned_data['confirm_password']
            avatar = form.cleaned_data['avatar']
            if password and password != password_doublecheck:
                raise ValidationError("Passwords don't match")
            new_user = User.objects.create_user(username, email, password)
            new_profile = UserProfile()

            new_profile = UserProfile.objects.get(user__username=username)
            new_profile.user.first_name = first_name
            new_profile.user.last_name = last_name
            new_profile.user.save()

            new_profile.gender = gender
            new_profile.date_of_birth = date_of_birth
            new_profile.avatar = avatar
            new_profile.save()

        return redirect(reverse('index'))

def login_view(request):
    if request.method == 'GET':
        login_form = UserLogin()
        context = {
            'form': login_form,
        }
        return render(request, 'login.html', context)
    if request.method == 'POST':
        login_form = UserLogin(request.POST)
        #try to change to .cleaned data
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            context = {
                'form': login_form,
                'message': 'Wrong user and/or password!',
            }
            return render(request, 'login.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse('login'))


@login_required
def profile_view(request, user):
    profile = UserProfile.objects.get(user__username=user)
    posts = UserPost.objects.filter(author=request.user)
    context = {
        'profile': profile,
        'posts': posts
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile_view(request, user):
    profile = UserProfile.objects.get(user__username=user)
    if not request.user == profile.user:
        return HttpResponseForbidden()
    if request.method == 'GET':
        data = {
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'gender': profile.gender,
            'date_of_birth': profile.date_of_birth,
        }
        avatar = SimpleUploadedFile(
            profile.avatar.name, profile.avatar.file.read()) \
            if profile.avatar else None
        file_data = {'avatar': avatar}
        form = UserProfileForm(data, file_data)
    elif request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile.user.first_name = form.cleaned_data['first_name']
            profile.user.last_name = form.cleaned_data['last_name']
            profile.user.save()

            profile.gender = form.cleaned_data['gender']
            profile.date_of_birth = form.cleaned_data['date_of_birth']
            if form.cleaned_data['avatar']:
                profile.avatar = form.cleaned_data['avatar']
            profile.save()

            return redirect(reverse('profile', args=[profile.user.username]))
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'edit_profile.html', context)


@login_required
def like_view(request, pk):
    post = UserPost.objects.get(pk=pk)
    post.likers.add(request.user)
    post.save()
    return redirect(reverse('post_details', args=[post.pk]))

@login_required
def add_friends_l(request, pk):
    friend_profile = UserProfile.objects.get(user__id=pk)
    user_profile = request.user.profile
    user_profile.friends.add(friend_profile)
    user_profile.save()
    return redirect(reverse('add_friends_p'))
    
@login_required    
def add_friends_p(request):
    users = User.objects.exclude(pk=request.user.pk).exclude(profile__in=request.user.profile.friends.all())
    context = {
	'users': users
    } 
    return render(request, 'add_friends.html', context)
    

