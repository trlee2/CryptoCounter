from django import forms

# Registration Page Form
class UserRegistrationForm(forms.Form):
    firstName = forms.CharField(
        required = True,
        label = 'First Name',
        max_length = 32,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'})
    )
    lastName = forms.CharField(
        required = True,
        label = 'Last Name',
        max_length = 32,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'})
    )
    email = forms.EmailField(
        required = True,
        label = 'Email',
        max_length = 50,
        widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'})
    )
    username = forms.CharField(
        required = True,
        label = 'Username',
        max_length = 32,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'})
    )
    password = forms.CharField(
        required = True,
        label = 'Password',
        max_length = 32,
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'})
    )
    confirmPassword = forms.CharField(
        required = True,
        label = 'Confirm Password',
        max_length = 32,
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'})
    )

# login form
class UserLoginForm(forms.Form):
    username = forms.CharField(
        required = True,
        label = 'Username',
        max_length = 32,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'})
    )
    password = forms.CharField(
        required = True,
        label = 'Password',
        max_length = 32,
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'})
    )
#search bar form
class CoinSearchForm(forms.Form):
    term = forms.CharField(
        required = True,
        label = 'Search',
        max_length = 50,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Search'})
    )
