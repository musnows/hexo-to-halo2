import requests
import traceback
from slugify import slugify
from .MarkdownRender import render_markdown
from .JsonParse import open_json_file

# 注意，本代码中函数传入url地址中的部分的slug应该是posts信息中["metadata"]["name"]
# 因为调用api上传时已经将["spec"]["slug"]和["metadata"]["name"]维持一致了，所以在函数参数上没有做区分。
# 如果是在halo2控制台创建的文章，["spec"]["slug"]和["metadata"]["name"]可能不同，需要加以区分。

UserConfig = open_json_file("./config/config.json")
"""用户配置项目"""
assert ('published' in UserConfig)  # 配置检查

BASE_URL = UserConfig["haloSite"]
"""站点链接，不带尾随`/`斜杠"""
API_KEY = UserConfig["userToken"]
"""
用户API个人令牌，在个人中心中的个人令牌里面生成
"""
BASE_HEADER = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
"""基础请求头"""


def get_page_list():
    """获取所有文章的列表"""
    posts_url = f"/apis/api.console.halo.run/v1alpha1/posts"
    ret = requests.get(url=BASE_URL + posts_url,
                       headers=BASE_HEADER)  # 这里要用json来传data
    # print(ret.text)
    return ret.json()


def get_posts_info(slug: str):
    """
    获取单个文章的信息
    - slug: 文章详细信息中的["metadata"]["name"]
    - 注：可以通过所有文章列表API找到对应文章的该字段
    """
    ret = requests.get(url=BASE_URL +
                       f"/apis/content.halo.run/v1alpha1/posts/{slug}",
                       headers=BASE_HEADER)
    # print(ret.text)
    return ret.json()


def get_posts_content(slug: str):
    """
    获取单个文章的内容
    - slug: 文章详细信息中的["metadata"]["name"]
    - 注：可以通过所有文章列表API找到对应文章的该字段
    """
    ret = requests.get(
        url=BASE_URL +
        f"/apis/api.console.halo.run/v1alpha1/posts/{slug}/head-content",
        headers=BASE_HEADER)
    return ret.json()


def get_tags_list():
    """获取所有tag的列表"""
    ret = requests.get(url=BASE_URL + f"/apis/content.halo.run/v1alpha1/tags",
                       headers=BASE_HEADER)
    return ret.json()


def get_categories_list():
    """获取所有categories的列表"""
    ret = requests.get(url=BASE_URL +
                       f"/apis/content.halo.run/v1alpha1/categories",
                       headers=BASE_HEADER)
    return ret.json()


def update_page(slug: str,
                raw_content: str = "",
                title: str = "",
                cover: str = "",
                categories: list[str] = [],
                tags: list[str] = [],
                publish_time=None):
    """
    如果该文章已有，则调用update方法，slug必须是已有文章的永久name。
    
    除了slug外的参数可以为空，为空代表不更新。

    - slug: 文章永久链接（abbrlink）
    - raw_content：原始md文件
    - title: 文章标题
    - cover: 文章封面链接
    - categories: 文章分类（必须先创建分类并用返回值的["metadata"]["name"]来请求）
    - tags: 文章tag（必须先创建tags并用返回值的["metadata"]["name"]来请求）
    - publish_time: 更新时间（暂时没有找到调用方式）
    """
    # 注意两个接口的前缀url不同！
    posts_url = f"/apis/content.halo.run/v1alpha1/posts/{slug}"
    posts_url_content = f"/apis/api.console.halo.run/v1alpha1/posts/{slug}/content"
    # 先获取基本信息
    data = {}
    data["post"] = get_posts_info(slug)
    data["content"] = get_posts_content(slug)
    # 修改文章内容
    if raw_content != "":
        data["content"]["raw"] = raw_content
        data["content"]["content"] = render_markdown(raw_content)
    # 修改文章信息
    if title != "":
        data["post"]["spec"]["title"] = title
    if cover != "":
        data["post"]["spec"]["cover"] = cover
    if categories != []:
        data["post"]["spec"]["categories"] = categories
    if tags != []:
        data["post"]["spec"]["tags"] = tags
    if publish_time:
        data["post"]["spec"]["publishTime"] = publish_time

    # print(json.dumps(data, ensure_ascii=False), '\n')
    # 更新文章信息
    ret1 = requests.put(url=BASE_URL + posts_url,
                        json=data["post"],
                        headers=BASE_HEADER)  # 这里要用json来传data
    # 更新文章内容
    ret2 = requests.put(url=BASE_URL + posts_url_content,
                        json=data["content"],
                        headers=BASE_HEADER)  # 这里要用json来传data
    return (ret1.json(), ret2.json())


def post_page(raw_content: str,
              title: str,
              slug: str,
              cover: str,
              categories: list[str],
              tags: list[str],
              pinned: bool = False,
              allow_comment: bool = True,
              is_public: bool = True,
              publish_time=None):
    """
    上传文章，使用本函数前需要在halo2中安装任意markdown编辑器插件

    - raw_content：原始md文件
    - title: 文章标题
    - slug: 文章永久链接（abbrlink）
    - cover: 文章封面链接
    - categories: 文章分类（必须先创建分类并用返回值的["metadata"]["name"]来请求）
    - tags: 文章tag（必须先创建tags并用返回值的["metadata"]["name"]来请求）
    - pinned: 是否置顶
    - allow_comment: 是否允许评论
    - is_public: 是否公开
    - publish_time: 更新时间（暂时没有找到调用方式）
    """
    try:
        posts_url = f"/apis/api.console.halo.run/v1alpha1/posts"
        data = {
            "post": {
                "spec": {
                    "title": title,
                    "slug": slug,
                    "template": "",
                    "cover": cover,
                    "deleted": False,
                    "publish": False,
                    "publishTime": publish_time,
                    "pinned": pinned,
                    "allowComment": allow_comment,
                    "visible": "PUBLIC" if is_public else "PRIVATE",
                    "priority": 0,
                    "excerpt": {
                        "autoGenerate": True,
                        "raw": ""
                    },
                    "categories": categories,
                    "tags": tags,
                    "htmlMetas": []
                },
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Post",
                "metadata": {
                    "name": slug
                }
            },
            "content": {
                "raw": raw_content,
                "content": render_markdown(raw_content),
                "rawType": "markdown"
            }
        }
        ret = requests.post(url=BASE_URL + posts_url,
                            json=data,
                            headers=BASE_HEADER)  # 这里要用json来传data
        # print(ret.text)
        return (ret.json(), {})
    except:
        print(traceback.format_exc())
        return (None, None)


def publish_page(slug: str):
    """发布文章"""
    publish_url = f"/apis/api.console.halo.run/v1alpha1/posts/{slug}/publish"
    ret = requests.put(url=BASE_URL + publish_url, headers=BASE_HEADER)
    # print(ret.text)
    return ret.json()


def unpublish_page(slug: str):
    """取消发布文章"""
    unpublish_url = f"/apis/api.console.halo.run/v1alpha1/posts/{slug}/unpublish"
    ret = requests.put(url=BASE_URL + unpublish_url, headers=BASE_HEADER)
    # print(ret.text)
    return ret.json()


def create_tag(name: str, color: str = "#ffffff", cover: str = ""):
    """
    创建tag

    注意：创建前应该先获取已有tag并判断是否有同名tag（否则会创建多个同名tag）

    - name: tag的名字
    - color: tag的颜色
    - cover: tag的展示封面
    """
    tags_url = "/apis/content.halo.run/v1alpha1/tags"
    data = {
        "spec": {
            "displayName": name,
            "slug": slugify(name),
            "color": color,
            "cover": cover,
        },
        "apiVersion": "content.halo.run/v1alpha1",
        "kind": "Tag",
        "metadata": {
            "name": "",
            "generateName": "tag-",
            "annotations": {}
        }
    }
    # print(data)
    ret = requests.post(url=BASE_URL + tags_url,
                        headers=BASE_HEADER,
                        json=data)
    return ret.json()


def create_category(name: str,
                    color: str = "#ffffff",
                    cover: str = "",
                    description: str = ""):
    """
    创建分组

    注意：创建前应该先获取已有分组并判断是否有同名分组（否则会创建多个同名分组）

    - name: category的名字
    - color: category的颜色
    - cover: category的展示封面
    - description: category的描述
    """
    category_url = "/apis/content.halo.run/v1alpha1/categories"
    data = {
        "spec": {
            "displayName": name,
            "slug": slugify(name),
            "color": color,
            "cover": cover,
            "description": description,
            "template": "",
            "priority": len(name),
            "children": []
        },
        "apiVersion": "content.halo.run/v1alpha1",
        "kind": "Category",
        "metadata": {
            "name": "",
            "generateName": "category-",
            "annotations": {}
        }
    }
    ret = requests.post(url=BASE_URL + category_url,
                        headers=BASE_HEADER,
                        json=data)
    return ret.json()
