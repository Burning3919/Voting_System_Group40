from django import forms
from .models import Customer
from django.forms import modelformset_factory
from .models import Poll, Option
class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("密码不匹配")

        return cleaned_data


class CustomerLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email']




class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'cut_off', 'active']




class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'cut_off', 'active']

# 选项表单集合 ✅【新增】
OptionFormSet = modelformset_factory(Option, fields=('content',), extra=1)
