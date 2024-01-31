import requests
import traceback
from slugify import slugify
from .MarkdownRender import render_markdown
from .JsonParse import open_json_file

UserConfig = open_json_file("./config/config.json")
"""用户配置项目"""
assert('published' in UserConfig) # 配置检查

BASE_URL = UserConfig["haloSite"]
# 在个人中心中的个人令牌里面生成
API_KEY = UserConfig["userToken"]
BASE_HEADER = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


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
    - categories: 文章分类
    - tags: 文章tag
    - pinned: 是否置顶
    - allow_comment: 是否允许评论
    - is_public: 是否公开
    - publish_time: 更新时间（暂时没有找到调用方式）
    """
    try:
        post_url = f"/apis/api.console.halo.run/v1alpha1/posts"
        data = {
            "post": {
                "spec": {
                    "title": title,
                    "slug": slug,
                    "template": "",
                    "cover": cover,
                    "deleted": False,
                    "publish": False,
                    "publishTime": None,
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
        ret = requests.post(url=BASE_URL + post_url,
                            json=data,
                            headers=BASE_HEADER)  # 这里要用json来传data
        # print(ret.text)
        return ret.json()
    except:
        print(traceback.format_exc())
        return {}


def publish_page(slug: str):
    """发布文章"""
    try:
        publish_url = f"/apis/api.console.halo.run/v1alpha1/posts/{slug}/publish"
        ret = requests.put(url=BASE_URL + publish_url, headers=BASE_HEADER)
        # print(ret.text)
        return ret.json()
    except:
        print(traceback.format_exc())
        return {}


def unpublish_page(slug: str):
    """取消发布文章"""
    try:
        unpublish_url = f"/apis/api.console.halo.run/v1alpha1/posts/{slug}/unpublish"
        ret = requests.put(url=BASE_URL + unpublish_url, headers=BASE_HEADER)
        # print(ret.text)
        return ret.json()
    except:
        print(traceback.format_exc())
        return {}


def create_tag(name: str, color: str = "#ffffff", cover: str = ""):
    """创建tag
    - name: tag的名字
    - color: tag的颜色
    - cover: tag的展示封面
    """
    try:
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
    except:
        print(traceback.format_exc())
        return {}


def create_category(name: str,
                    color: str = "#ffffff",
                    cover: str = "",
                    description: str = ""):
    """创建分组
    
    - name: category的名字
    - color: category的颜色
    - cover: category的展示封面
    - description: category的描述
    """
    try:
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
    except:
        print(traceback.format_exc())
        return {}
