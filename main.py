import os
import time
import traceback
import sys
from utils import FormatterParse, Halo2Uploader


def get_files_list(dir: str):
    """
    获取一个目录下所有文件列表，包括子目录
    - dir: 文件路径
    """
    files_list = []
    for root, dirs, files in os.walk(dir, topdown=False):
        for file in files:
            files_list.append(os.path.join(root, file))

    return files_list


def args_checker():
    """参数检查器"""
    if len(sys.argv) != 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)
    # 获取命令行参数
    input_value = sys.argv[1]
    return input_value


def main(folder_path: str):
    """遍历处理文件夹中的所有md文件"""
    print("[begin]", folder_path)
    i = 0
    file_list = get_files_list(folder_path)
    tag_dict, category_dict = {}, {}
    for md_file_path in file_list:
        try:
            tag_list, category_list = [], []
            # 读取文件
            with open(md_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 解析frontmatter
            frontmatter_dict = FormatterParse.parse_markdown_frontmatter(
                content)
            print(i, '[frontmatter]', frontmatter_dict)
            # frontmatter不存在
            if not frontmatter_dict:
                print(i, "[ERROR] this file doesn't have frontmatter!",
                      md_file_path)
                continue
            # 有这个字段代表需要置顶
            if_pinned = ('sticky' in frontmatter_dict)
            # 如果没有cover则添加一个空字符串
            if 'cover' not in frontmatter_dict:
                frontmatter_dict['cover'] = ""
            # 上传时去除md文件中的frontmatter
            content = FormatterParse.remove_frontmatter(content)

            # 创建halo2中的tag和分类
            for tag in frontmatter_dict['tags']:
                if tag not in tag_dict:
                    tag_ret = Halo2Uploader.create_tag(tag)
                    print(i, '[tag]', tag_ret)
                    tag_dict[tag] = tag_ret
                    time.sleep(0.1)

                tag_list.append(tag_dict[tag]['metadata']['name'])

            for cate in frontmatter_dict['categories']:
                if cate not in category_dict:
                    cate_ret = Halo2Uploader.create_category(cate)
                    print(i, '[category]', cate_ret)
                    category_dict[cate] = cate_ret
                    time.sleep(0.1)

                category_list.append(category_dict[cate]['metadata']['name'])

            # 这里的key都是从frontmatter中解析出来的
            # 如果你的hexo主题使用的frontmatter不同，可以修改这里的key值
            if 'abbrlink' in frontmatter_dict:
                slug = frontmatter_dict['abbrlink']
            else:
                slug = Halo2Uploader.slugify(frontmatter_dict['title'])
            # 上传时间解析，可以参考posts接口get返回值中的格式进行解析
            # "publishTime": "2024-01-22T05:12:33.716773059Z"
            publish_time = None
            if 'date' in frontmatter_dict:
                microseconds_str = f"{frontmatter_dict['date'].microsecond:0<9}" # 9位，不够的后补0
                publish_time = f"{frontmatter_dict['date'].strftime('%Y-%m-%dT%H:%M:%S')}.{microseconds_str}Z"
                print(i,"[publish_time]",publish_time)
            # 上传文章
            upload_ret = Halo2Uploader.post_page(
                content,
                frontmatter_dict['title'],
                slug,
                frontmatter_dict['cover'],
                category_list,
                tag_list,
                pinned=if_pinned,
                publish_time=publish_time)
            print(i, '[upload]', upload_ret)
            # 发布文章
            if Halo2Uploader.UserConfig['published']:
                publish_ret = Halo2Uploader.publish_page(
                    frontmatter_dict['abbrlink'])
            print(i, '[publish]', publish_ret)
            i += 1
            time.sleep(0.1)
        except:
            print("[ERROR] exception occur when handling", md_file_path)
            print(traceback.format_exc())
            time.sleep(0.1)
            continue

    print("[finished]", folder_path)


if __name__ == '__main__':
    folder_path = args_checker()
    main(folder_path)
