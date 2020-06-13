# __author = wulinjun
# date:2020/6/8 23:39


from django.urls import reverse
from django import template
from django.http import QueryDict

register = template.Library()


@register.simple_tag
def reverse_url(request):
    if request.path == reverse('customers'):
        return '公户信息'
    else:
        return '我的客户信息'


# 编辑完跳转回原路径
@register.simple_tag
def resole_url(request, url_name, customer_pk):
    next_url = request.get_full_path()
    reverse_url = reverse(url_name, args=(customer_pk,))
    q = QueryDict(mutable=True)
    q['next'] = next_url
    next_url = q.urlencode()
    full_url = reverse_url + '?' + next_url
    return full_url
