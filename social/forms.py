from django import forms
from .models import Post, Profile, Comment
from django.contrib.auth.models import User


class PostCreateForm(forms.ModelForm):
    body = forms.CharField(label="Body", widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your thoughts goes here', 'rows': '4', 'cols': '25'}))
    class Meta:
        model = Post
        fields = (
            "title",
            "body",
            "status",
            'restrict_comment'
            )

class PostEditForm(forms.ModelForm):
    body = forms.CharField(label="Body", widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your thoughts goes here', 'rows': '4', 'cols': '25'}))
    class Meta:
        model = Post
        fields = (
            "title",
            "body",
            "status",
            'restrict_comment'
            )

class UserLoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs= {'placeholder': 'Enter Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs= {'placeholder': 'Confirm Password'}))
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email'
        )

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if len(password) and len(confirm_password) <= 4:
            raise forms.ValidationError("Password length should be greater than 4 digits")

        if password != confirm_password:
            raise forms.ValidationError('Password Mismatch')
        return confirm_password


class UserEditForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email'
        )

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)

class CommentForm(forms.ModelForm):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Comments goes here', 'rows': '4', 'cols': '25'}))
    class Meta:
        model = Comment
        fields = ('content',)