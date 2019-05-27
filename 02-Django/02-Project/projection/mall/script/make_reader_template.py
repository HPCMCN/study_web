# coding = utf-8
from collections import OrderedDict

from content.models import ContentCategory
from contents.index.index import GENERATED_STATIC_HTML_FILES_DIR
from goods.models import GoodsChannel


def reader_index_template():
    """渲染主页"""
    categories = OrderedDict()
    # 获取一级分类
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')

    # 对一级分类进行遍历
    for channel in channels:
        # 获取group_id
        group_id = channel.group_id
        # 判断group_id 是否在存储容器,如果不在就初始化
        if group_id not in categories:
            categories[group_id] = {
                'channels': [],
                'sub_cats': []
            }

        one = channel.category
        # 为channels填充数据
        categories[group_id]['channels'].append({
            'id': one.id,
            'name': one.name,
            'url': channel.url
        })
        # 为sub_cats填充数据
        for two in one.goodscategory_set.all():
            # 初始化 容器
            two.sub_cats = []
            # 遍历获取
            for three in two.goodscategory_set.all():
                two.sub_cats.append(three)

            # 组织数据
            categories[group_id]['sub_cats'].append(two)

    contents = {}
    content_categories = ContentCategory.objects.all()
    # content_categories = [{'name':xx , 'key': 'index_new'}, {}, {}]

    # {
    #    'index_new': [] ,
    #    'index_lbt': []
    # }
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    context = {
        'categories': categories,
        'contents': contents
    }
    from django.template import loader
    # 1. 首先得到模版
    render_html = loader.get_template('index.html')
    # 2. 将数据渲染到模板中
    html_data = render_html.render(context)
    index_path_file = GENERATED_STATIC_HTML_FILES_DIR + "/index.html"
    # 3. 将数据流写入到文件中保存起来方便使用
    with open(index_path_file, "w") as f:
        f.write(html_data)
    print("加载%s" % group_id)
