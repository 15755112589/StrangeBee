from django.db import models
from multiselectfield import MultiSelectField
from django.utils.safestring import mark_safe


# Create your models here.


class UserInfo(models.Model):
    """
    用户表
    """
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=32)
    email = models.EmailField()
    telephone = models.CharField(max_length=16)
    is_active = models.BooleanField(default=True)

    def __str__(self):

        return self.username


source_type = (
    ('qq', 'qq群'),
    ('referral', '内部转介绍'),
    ('website', '官方网站'),
    ('baidu_ads', '百度推广'),
    ('office_direct', '直接上门'),
    ('WoM', '口碑'),
    ('public_class', '公开课'),
    ('website_luffy', '路飞官网'),
    ('others', '其它'),
)

course_choices = (
    ('LinuxL', 'Linux中高级'),
    ('PythonFullStack', 'Python高级全栈开发')
)

class_type_choices = (
    ('fulltime', '脱产班'),
    ('online', '网络班'),
    ('weekend', '周末班'),
)

enroll_status_choices = (
    ('signed', '已报名'),
    ('unregistered', '未报名'),
    ('studying', '学习中'),
    ('paid_in_full', '学费已交齐'),
)

seek_status_choices = (('A', '近期无报名计划'), ('B', '1个月内报名'), ('C', '2周内报名'), ('D', '1周内报名'),
                       ('E', '定金'), ('F', '到班'), ('G', '全款'), ('H', '无效'),)


class Customer(models.Model):
    """
    客户表
    """
    qq = models.CharField("QQ", max_length=64, unique=True, help_text="QQ号必须唯一")
    qq_name = models.CharField("QQ昵称", max_length=64, blank=True, null=True)
    name = models.CharField("姓名", max_length=32, blank=True, null=True, help_text="学生报名后，名字改为真实姓名")
    sex_type = (('male', '男'), ('female', '女'))
    sex = models.CharField("性别", choices=sex_type, max_length=16, default='male', blank=True, null=True)
    birthday = models.DateField('出生日期', default=None, help_text="格式yyyy-mm-dd", blank=True, null=True)
    phone = models.BigIntegerField("手机号", blank=True, null=True)
    source = models.CharField("客户来源", max_length=64, choices=source_type, default="qq")
    introduce_from = models.ForeignKey("self", verbose_name="转介绍自学员", blank=True, null=True, on_delete=models.CASCADE)
    course = MultiSelectField("咨询课程", choices=course_choices)  # 多选，并且存成一个列表,通过ModelForm来用的时候，会成为多选框
    class_type = models.CharField("班级类型", max_length=64, choices=class_type_choices, default='fulltime')
    customer_note = models.TextField("客户备注", blank=True, null=True)
    status = models.CharField("状态", choices=enroll_status_choices, max_length=64, default='unregistered',
                              help_text='选择客户此时的状态')
    date = models.DateTimeField("咨询日期", auto_now_add=True)  # 这个没啥用昂，销售说是为了一周年的时候给客户发一个祝福信息啥的
    last_consult_date = models.DateField("最后跟进日期", auto_now_add=True)  # 考核销售的跟进情况，如果多天没有跟进，会影响销售的绩效等
    next_date = models.DateField("预计再次跟进时间", blank=True, null=True)  # 销售自己大概记录一下自己下一次会什么时候跟进，也没啥用
    # 用户表中存放的是自己公司的所有员工。
    consultant = models.ForeignKey('UserInfo', verbose_name="销售", related_name='customers', blank=True, null=True,
                                   on_delete=models.CASCADE)
    # 一个客户可以报多个班，报个脱产班，再报个周末班等，所以是多对多。
    class_list = models.ManyToManyField('ClassList', verbose_name="已报班级", blank=True)

    # 配置给127.0.0.1/admin使用
    class Meta:
        ordering = ['id', ]
        verbose_name = '客户信息表'
        verbose_name_plural = '客户信息表'

    def __str__(self):
        return self.name + ":" + self.qq

    def status_show(self):
        status_color = {
            'unregistered': 'red',
            'signed': 'orange',
            'studying': 'yellow',
            'paid_in_full': 'green'
        }

        return mark_safe("<span style='background-color: {0}'>{1}</span>".format(status_color[self.status], self.get_status_display()))


class ClassList(models.Model):
    """
    班级表
    """
    course = models.CharField("课程名称", max_length=64, choices=course_choices)
    semester = models.IntegerField("学期")  # python20期等
    campuses = models.ForeignKey('Campuses', verbose_name="校区", on_delete=models.CASCADE)
    price = models.IntegerField("学费", default=10000)
    memo = models.CharField('说明', blank=True, null=True, max_length=100)
    start_date = models.DateField("开班日期")
    graduate_date = models.DateField("结业日期", blank=True, null=True)  # 不一定什么时候结业，哈哈，所以可为空

    teachers = models.ManyToManyField('UserInfo', verbose_name="老师")  # 对了，还有一点，如果你用的django2版本的，那么外键字段都需要自行写上on_delete=models.CASCADE

    class_type = models.CharField(choices=class_type_choices, max_length=64, verbose_name='班级及类型', blank=True,
                                  null=True)

    class Meta:
        unique_together = ("course", "semester", "campuses")

    def __str__(self):
        return '{}{}({})'.format(self.get_course_display(), self.semester, self.campuses)


class Campuses(models.Model):
    """
    校区表
    """
    name = models.CharField(verbose_name='校区', max_length=64)
    address = models.CharField(verbose_name='详细地址', max_length=512, blank=True, null=True)

    def __str__(self):
        return self.name


class ConsultRecord(models.Model):
    """
    跟进记录表
    """
    customer = models.ForeignKey('Customer', verbose_name='所咨询客户')
    note = models.TextField(verbose_name='跟进内容')
    status = models.CharField('跟进状态', max_length=8, choices=seek_status_choices, help_text='选择客户此时的状态')
    consultant = models.ForeignKey("UserInfo", verbose_name="跟进人", related_name='records')
    date = models.DateTimeField("跟进日期", auto_now_add=True)
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)


class Enrollment(models.Model):
    """
    报名表
    """
    why_us = models.TextField("为什么报名", max_length=1024, default=None, blank=True, null=True)
    your_expectation = models.TextField("学完想达到的具体期望", max_length=1024, blank=True, null=True)
    # contract_agreed = models.BooleanField("我已认真阅读完培训协议并同意全部协议内容", default=False)
    contract_approved = models.BooleanField("审批通过", help_text="在审阅完学员的资料无误后勾选此项,合同即生效", default=False)
    enrolled_date = models.DateTimeField(auto_now_add=True, verbose_name="报名日期")
    memo = models.TextField('备注', blank=True, null=True)
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)
    customer = models.ForeignKey('Customer', verbose_name='客户名称')
    school = models.ForeignKey('Campuses')
    enrolment_class = models.ForeignKey("ClassList", verbose_name="所报班级")

    class Meta:
        unique_together = ('enrolment_class', 'customer')

    def __str__(self):
        return self.customer.name


