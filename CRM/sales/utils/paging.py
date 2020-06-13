# __author = wulinjun
# date:2020/6/6 15:21


# 自定义分页
class PageInfo(object):

    def __init__(self, current_page, all_count, per_page, base_url, get_data=None, show_page=5):
        """

        :param current_page: 当前页码
        :param get_data:  搜索条件
        :param all_count: 所有数据
        :param per_page:  每页展示的数据
        :param base_url:
        :param show_page:
        """
        try:
            self.current_page = int(current_page)

        except Exception as e:
            self.current_page = 1
        self.get_data = get_data
        self.per_page = per_page
        a, b = divmod(all_count, per_page)
        if b:
            a += 1
        self.all_pager = a
        self.show_page = show_page
        self.base_url = base_url

    def start(self):
        return (self.current_page - 1) * self.per_page

    def end(self):
        return self.current_page * self.per_page

    def pager(self):
        page_list = []

        half = int((self.show_page - 1) / 2)
        if self.all_pager < self.show_page:
            begin = 1
            stop = self.all_pager + 1
        # 如果当前页<=5，永远显示1，11
        else:
            if self.current_page <= half:
                begin = 1
                stop = self.show_page + 1
            else:
                if self.current_page + half > self.all_pager:
                    begin = self.all_pager - self.show_page + 1
                    stop = self.all_pager + 1
                else:
                    begin = self.current_page - half
                    stop = self.current_page + half + 1

        self.get_data['page'] = 1
        first_page = "<li><a href='%s?%s'>首页</a></li>" % (self.base_url, self.get_data.urlencode())
        page_list.append(first_page)
        if self.current_page <= 1:
            prev = "<li><a href='#'>上一页</a></li>"
        else:
            self.get_data['page'] = self.current_page - 1
            prev = "<li><a href='%s?%s'>上一页</a></li>" % (self.base_url, self.get_data.urlencode())
        page_list.append(prev)

        for i in range(begin, stop):
            if i == self.current_page:
                self.get_data['page'] = i
                v = "<li class='active'><a href='%s?%s'>%s</a></li>" % (self.base_url, self.get_data.urlencode(), i)
            else:
                self.get_data['page'] = i
                v = "<li><a href='%s?%s'>%s</a></li>" % (self.base_url, self.get_data.urlencode(), i)
            page_list.append(v)

        if self.current_page >= self.all_pager:
            nex = "<li><a href='#'>下一页</a></li>"
        else:
            self.get_data['page'] = self.current_page + 1
            nex = "<li><a href='%s?%s'>下一页</a></li>" % (self.base_url, self.get_data.urlencode())
        page_list.append(nex)
        self.get_data['page'] = self.all_pager
        last_page = "<li><a href='%s?%s'>尾页</a></li>" % (self.base_url, self.get_data.urlencode())
        page_list.append(last_page)
        return ''.join(page_list)
