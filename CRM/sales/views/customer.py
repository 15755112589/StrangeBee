# __author = wulinjun
# date:2020/6/10 1:04

from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.views import View

from sales import models
from sales.myforms import CustomerForm
from sales.utils.paging import PageInfo


# Create your views here.

# 首页
def home(request):
    return render(request, 'saleshtml/home.html')


# 公私户相关信息验证
class CustomerView(View):

    def get(self, request):

        current_request_path = request.path
        # 公户
        if current_request_path == reverse('customers'):
            tag = '1'
            customer_list = models.Customer.objects.filter(consultant__isnull=True)
        # 私户请求
        else:
            tag = '2'
            user_obj = request.user_obj
            customer_list = models.Customer.objects.filter(consultant=user_obj)

        get_data = request.GET.copy()  # 获取get请求提交的数据

        # 当前页
        current_page = request.GET.get('page')  # 当前页码
        kw = request.GET.get('kw')  # 查询关键字
        search_field = request.GET.get('search_field')
        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field, kw))
            customer_list = customer_list.filter(q_obj)
        else:
            customer_list = customer_list

        try:
            current_page = int(current_page)

        except Exception as e:
            current_page = 1

        # 每页显示的个数
        per_page = 10

        start_show = (current_page - 1) * per_page
        end_show = current_page * per_page
        # 每页显示的数据
        customers_obj = customer_list.reverse()[start_show: end_show]
        all_count = customer_list.count()
        page_info = PageInfo(current_page=current_page, all_count=all_count, per_page=per_page, get_data=get_data,
                             base_url=request.path,
                             show_page=5)
        return render(request, 'saleshtml/customers.html', {'customers_obj': customers_obj, 'page_info': page_info, 'tag': tag})

    def post(self, request):

        action = request.POST.get('action')
        cids = request.POST.getlist('cids')
        if hasattr(self, action):

            ret = getattr(self, action)(request, cids)
            if ret:
                return ret
            return redirect(request.path)

    # 公转私
    def reverse_gs(self, request, cids):
        customers = models.Customer.objects.filter(pk__in=cids, consultant__isnull=True)
        if customers.count() != len(cids):
            return HttpResponse('公转私失败，请刷新页面重新尝试！！')
        customers.update(consultant_id=request.session.get('user_id'))

    # 私转公
    def reverse_sg(self, request, customers):

        customers.update(consultant=None)


# 添加和编辑客户
def add_edit_customers(request, cid=None):
    """
    添加和编辑客户
    :param request:
    :return:
    """
    label = "编辑页面" if cid else "添加页面"
    customer_obj = models.Customer.objects.filter(pk=cid).first()
    if request.method == 'GET':
        customer_form = CustomerForm(instance=customer_obj)
        return render(request, 'saleshtml/edit_customers.html', {'customer_form': customer_form, 'label': label})

    else:
        next_url = request.GET.get('next')
        customer_form = CustomerForm(request.POST, instance=customer_obj)
        if customer_form.is_valid():
            customer_form.save()
            if next_url:
                return redirect(next_url)
            else:
                return redirect('customers')
        else:
            return render(request, 'saleshtml/edit_customers.html', {'customer_form': customer_form, 'label': label})


# 跟进记录
class ConsultRecord(View):

    def get(self, request):

        # 当前登录用户的未删除的客户的跟进记录
        consult_list = models.ConsultRecord.objects.filter(consultant=request.user_obj, delete_status=False)

        return render(request, 'saleshtml/consultrecord.html', {'consult_list': consult_list})


