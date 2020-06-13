# __author = wulinjun
# date:2020/6/10 1:04


import re

from django import forms
from django.core.exceptions import ValidationError

from sales import models


# 手机号校验规则
def mobile_validate(value):
    """
    手机号校验规则
    :param value:
    :return:
    """
    mobile_re = re.compile(r'^(13[0-9]|15[0123456789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    if not mobile_re.match(value):
        raise ValidationError('手机号码格式错误')


# 注册Form组件
class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=16,
        min_length=4,
        label='用户名',
        widget=forms.widgets.TextInput(attrs={'class': 'username', 'autocomplete': 'off', 'placeholder': "您的用户名"}),
        error_messages={
            'required': '用户名不能为空',
            'max_length': '用户名不能超过32位',
            'min_length': '用户名不能小于6位'
        }
    )

    password = forms.CharField(
        max_length=16,
        min_length=4,
        label='密码',
        widget=forms.widgets.PasswordInput(
            attrs={'class': 'password', "placeholder": "输入密码", "oncontextmenu": "return false",
                   "onpaste": "return false"}),
        error_messages={
            'required': '密码不能为空',
            'max_length': '密码不能超过32位',
            'min_length': '密码不能小于6位'
        }
    )

    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.widgets.PasswordInput(attrs={'class': 'password', "placeholder": "再次输入密码",
                                                  "oncontextmenu": "return false", "onpaste": "return false"}),
        error_messages={
            'required': '确认密码不能为空',
        }
    )

    email = forms.EmailField(
        label="邮箱",
        error_messages={
            'required': '邮箱不能为空',
            'invalid': '邮箱格式不对'
        },
        widget=forms.widgets.TextInput(attrs={'class': 'email', "placeholder": "输入邮箱地址",
                                              "oncontextmenu": "return false", "onpaste": "return false",
                                              "autocomplete": "off"}),
    )

    telephone = forms.CharField(
        label="手机号码",
        error_messages={
            'required': '手机号码不能为空'
        },
        validators=[mobile_validate, ],
        widget=forms.widgets.TextInput(attrs={'class': 'phone_number', "placeholder": "输入手机号码",
                                              "oncontextmenu": "return false", "onpaste": "return false",
                                              "autocomplete": "off"}),

    )

    def clean(self):
        values = self.cleaned_data
        password = values.get('password')
        confirm_password = values.get('confirm_password')

        if password == confirm_password:
            return values
        else:
            self.add_error('confirm_password', '两次输入的密码不一致')


# 客户相关信息验证
class CustomerForm(forms.ModelForm):

    class Meta:
        model = models.Customer
        fields = '__all__'

        error_message = {
            'qq': {'required': '不能为空'},
            'course': {'required': '不能为空'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from multiselectfield.forms.fields import MultiSelectFormField
        for field_name, field in self.fields.items():
            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})




