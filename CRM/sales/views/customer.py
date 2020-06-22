# __author = wulinjun
# date:2020/6/10 1:04
from django.conf import settings
from django.db.models import Q
from django.db import transaction
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.views import View

from sales import models
from sales.myforms import (CustomerForm, ConsultRecordForm, EnrollForm)
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
        return render(request, 'saleshtml/customers.html',
                      {'customers_obj': customers_obj, 'page_info': page_info, 'tag': tag})

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

        with transaction.atomic():
            customers = models.Customer.objects.filter(pk__in=cids, consultant__isnull=True)
        if customers.count() != len(cids):
            return HttpResponse('公转私失败，请刷新页面重新尝试！！')
        customers.update(consultant_id=request.session.get('user_id'))

    # 私转公
    def reverse_sg(self, request, cids):
        customers = models.Customer.objects.filter(pk__in=cids, consultant__isnull=False)
        if customers.count() != len(cids):
            return HttpResponse('私转公失败，请刷新页面重新尝试！！')
        customers.update(consultant=None)


# 添加和编辑客户信息
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

        cid = request.GET.get('cid')

        if cid:
            # 当前登录用户的未删除的客户的跟进记录
            consult_list = models.ConsultRecord.objects.filter(consultant=request.user_obj, delete_status=False,
                                                               customer_id=cid).order_by('-date')
        else:
            consult_list = models.ConsultRecord.objects.filter(consultant=request.user_obj,
                                                               delete_status=False).order_by('-date')

        # 分页和搜索
        get_data = request.GET.copy()  # 获取get请求提交的数据

        # 当前页
        current_page = request.GET.get('page')  # 当前页码
        kw = request.GET.get('kw')  # 查询关键字
        search_field = request.GET.get('search_field')
        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field, kw))
            consult_list = consult_list.filter(q_obj)
        else:
            consult_list = consult_list

        try:
            current_page = int(current_page)

        except Exception as e:
            current_page = 1

        # 每页显示的个数
        per_page = 10

        start_show = (current_page - 1) * per_page
        end_show = current_page * per_page
        # 每页显示的数据
        consult_obj = consult_list.reverse()[start_show: end_show]
        all_count = consult_list.count()
        page_info = PageInfo(current_page=current_page, all_count=all_count, per_page=per_page, get_data=get_data,
                             base_url=request.path,
                             show_page=5)
        return render(request, 'saleshtml/consultrecord.html',
                      {'consult_list': consult_obj, 'page_info': page_info})

    def post(self, request):
        action = request.POST.get('action')
        cids = request.POST.getlist('cids')
        if hasattr(self, action):
            consults = models.ConsultRecord.objects.filter(pk__in=cids)
            # print(customers)
            getattr(self, action)(request, consults)
            return redirect(request.path)

    # 公转私
    def bulk_delete(self, request, consults):
        consults.update(delete_status=True)


# 新增和编辑客户记录
class AddEditConsultView(View):

    def get(self, request, cid=None):

        """
            添加客户和编辑客户
            :param request:
            :param cid:   客户记录id
            :return:
            """
        label = '编辑跟进记录' if cid else '添加跟进记录'
        consult_obj = models.ConsultRecord.objects.filter(pk=cid).first()

        if request.method == 'GET':
            consult_form = ConsultRecordForm(request, instance=consult_obj)
            return render(request, 'saleshtml/add_edit_consult.html', {'consult_form': consult_form, 'label': label})

    def post(self, request, cid=None):
        consult_obj = models.ConsultRecord.objects.filter(pk=cid).first()
        next_url = request.GET.get('next')
        if not next_url:
            next_url = reverse('consult_record')
        consult_form = ConsultRecordForm(request, request.POST, instance=consult_obj)
        if consult_form.is_valid():
            consult_form.save()

            return redirect(next_url)
        else:
            return render(request, 'saleshtml/add_edit_consult.html', {'consult_form': consult_form})


# 删除单条跟进记录
def delete_consult_record(request, cid):
    models.ConsultRecord.objects.filter(pk=cid).update(delete_status=True)
    return redirect('consult_record')


# 报名记录展示
class EnrollmentView(View):

    def get(self, request):

        cid = request.GET.get('cid')
        if cid:
            # 当前登录用户的未删除的客户的跟进记录
            enroll_list = models.Enrollment.objects.filter(customer__consultant=request.user_obj, delete_status=False,
                                                               customer_id=cid).order_by('-enrolled_date')
        else:
            enroll_list = models.Enrollment.objects.filter(customer__consultant=request.user_obj,
                                                               delete_status=False).order_by('-enrolled_date')
        # 分页和搜索
        get_data = request.GET.copy()  # 获取get请求提交的数据

        # 当前页
        current_page = request.GET.get('page')  # 当前页码
        kw = request.GET.get('kw')  # 查询关键字
        search_field = request.GET.get('search_field')
        if kw:
            kw = kw.strip()
            q_obj = Q()
            q_obj.children.append((search_field, kw))
            enroll_list = enroll_list.filter(q_obj)
        else:
            enroll_list = enroll_list

        try:
            current_page = int(current_page)

        except Exception as e:
            current_page = 1

        # 每页显示的个数
        per_page = 10

        start_show = (current_page - 1) * per_page
        end_show = current_page * per_page
        # 每页显示的数据
        enroll_obj = enroll_list.reverse()[start_show: end_show]
        all_count = enroll_list.count()
        page_info = PageInfo(current_page=current_page, all_count=all_count, per_page=per_page, get_data=get_data,
                             base_url=request.path,
                             show_page=5)
        return render(request, 'saleshtml/enrollments.html',
                      {'enrolls': enroll_obj, 'page_info': page_info})

    def post(self, request):
        action = request.POST.get('action')
        cids = request.POST.getlist('cids')
        if hasattr(self, action):
            enrolls = models.Enrollment.objects.filter(pk__in=cids)
            getattr(self, action)(request, enrolls)
            return redirect(request.path)

    # 批量删除报名记录
    def bulk_enroll_record(self, request, enrolls):
        # enrolls.update(delete_status=True)
        enrolls.delete()


# 新增和编辑报名记录
class AddEditEnrollView(View):

    def get(self, request, cid=None):

        """
            添加报名记录和编辑报名记录
            :param request:
            :param cid:   客户记录id
            :return:
            """
        label = '编辑报名记录' if cid else '添加报名记录'
        enroll_obj = models.Enrollment.objects.filter(pk=cid).first()
        if request.method == 'GET':
            enroll_form = EnrollForm(request, instance=enroll_obj)
            return render(request, 'saleshtml/add_edit_enroll.html', {'enroll_form': enroll_form, 'label': label})

    def post(self, request, cid=None):
        enroll_obj = models.Enrollment.objects.filter(pk=cid).first()
        next_url = request.GET.get('next')
        enroll_form = EnrollForm(request, request.POST, instance=enroll_obj)
        if enroll_form.is_valid():
            enroll_form.save()
            if not next_url:
                return redirect('enrollment')
            else:
                return redirect(next_url)
        else:
            return render(request, 'saleshtml/add_edit_enroll.html', {'enroll_form': enroll_form})


# 删除单条报名记录
def delete_enroll_record(request, cid):
    # models.Enrollment.objects.filter(pk=cid).update(delete_status=True)
    models.Enrollment.objects.filter(pk=cid).delete()
    return redirect('enrollment')
