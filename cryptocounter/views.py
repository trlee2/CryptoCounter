from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect
from django import forms
from .forms import UserRegistrationForm, UserLoginForm

# Create your views here.
def market(request):
    return render(request, 'cryptocounter/market.html')

def ico(request):
    return render(request, 'cryptocounter/ico.html')

def socialTrends(request):
    return render(request, 'cryptocounter/trends.html')

def watchlist(request):
    return render(request, 'cryptocounter/watchlist.html')

def login(request):
    if request.method == 'POST':
        # get form data
        form = UserLoginForm(request.POST)
        # clean the form data, checks for security risks
        if form.is_valid():
            # parse form data
            userObj = form.cleaned_data
            username = userObj['username']
            password = userObj['password']

            # Check credentials
            user = authenticate(username = username, password = password)
            if user is not None:
                # log the user in
                auth_login(request, user)
                # redirect to watchlist
                return HttpResponseRedirect('watchlist')
            else:
                raise forms.ValidationError('Username or password incorrect')
    else:
        form = UserLoginForm()
    return render(request, 'cryptocounter/index.html', {'form' : form})

def register(request):
    if request.method == 'POST':
        # get form data
        form = UserRegistrationForm(request.POST)
        # clean the form data, checks for security risks
        if form.is_valid():
            # parse form data
            userObj = form.cleaned_data
            firstName = userObj['firstName']
            lastName = userObj['lastName']
            email = userObj['email']
            username = userObj['username']
            password = userObj['password']
            confirmPassword = userObj['confirmPassword']

            # username in use
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Sorry, that username has already been taken!')
            # email in use
            elif User.objects.filter(email=email).exists():
                raise forms.ValidationError('Sorry, that email is already in use!')
            # create user
            else:
                newUser = User.objects.create_user(username, email, password)
                newUser.first_name = firstName
                newUser.last_name = lastName
                newUser.save()
                # log the user in
                user = authenticate(username = username, password = password)
                auth_login(request, user)
                # redirect to watchlist
                return HttpResponseRedirect('watchlist')
    else:
        form = UserRegistrationForm()
    return render(request, 'cryptocounter/register.html', {'form' : form})

def header(request):
    loggedin = request.user.is_authenticated
    return render(request, 'cryptocounter/header.html', {'loggedin' : loggedin})

def footer(request):
    return render(request, 'cryptocounter/footer.html')
