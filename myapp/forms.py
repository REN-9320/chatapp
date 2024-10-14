from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

class SignupForm(UserCreationForm):
    usable_password = None
    

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'image','password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            

class ChangeUsernameForm(forms.ModelForm):
    
    class Meta:
        model = CustomUser
        fields = ('username',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        
class ChangeEmailForm(forms.ModelForm):
    
    class Meta:
        model = CustomUser
        fields = ('email',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].help_text = None
        
        
class ChangeImageForm(forms.ModelForm):
    
    class Meta:
        model = CustomUser
        fields = ('image',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = None
        
class PasswordChangeForm(PasswordChangeForm):
    
   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
class SearchForm(forms.Form):
        keyword = forms.CharField(label='', max_length=50)