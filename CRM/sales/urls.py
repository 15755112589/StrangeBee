# __author = wulinjun
# date:2020/6/11 22:19


from django.conf.urls import url
from django.contrib import admin

from sales.views import auth
from sales.views import customer

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # 登录
    url(r'^login/', auth.login, name='login'),
    # 注册
    url(r'^register/', auth.register, name='register'),
    # 首页
    url(r'^home/', customer.home, name='home'),
    # 总客户信息页
    url(r'^customers/', customer.CustomerView.as_view(), name='customers'),
    # 我的客户信息页
    url(r'^mycustomers/', customer.CustomerView.as_view(), name='mycustomers'),

    # 添加客户
    # url(r'^add_customers/', views.add_customers, name='add_customers'),
    url(r'^add_customers/', customer.add_edit_customers, name='add_customers'),
    # 编辑客户
    # url(r'^edit_customers/(\d+)/', views.edit_customers, name='edit_customers'),
    url(r'^edit_customers/(\d+)/', customer.add_edit_customers, name='edit_customers'),

    # 跟进记录
    url(r'^consult_record', customer.ConsultRecord.as_view(), name='consult_record'),
    # 添加跟进记录
    url(r'^add_consult_record', customer.AddEditConsultView.as_view(), name='add_consult_record'),
    # 编辑跟进记录
    url(r'^edit_consult_record/(\d+)/', customer.AddEditConsultView.as_view(), name='edit_consult_record'),
    # 删除客户记录
    url(r'^delete_consult_record/(\d+)', customer.delete_consult_record, name='delete_consult_record'),

]





