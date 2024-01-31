import frontmatter


def parse_markdown_frontmatter(content: str):
    """解析md文件的frontmatter，按字段返回一个dict"""
    post = frontmatter.loads(content)

    # 将 front matter 转为字典
    front_matter_dict = dict(post)

    return front_matter_dict


def parse_markdown_frontmatter_file(md_file_path):
    """
    解析md文件的frontmatter，按字段返回一个dict
    - md_file_path: md文件路径
    """
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    return parse_markdown_frontmatter(content)


def remove_frontmatter(md_content: str):
    """去除md文件中的frontmatter部分"""
    # 查找第一个 '---' 的索引
    start_index = md_content.find('---')

    if start_index != -1:
        # 查找第二个 '---' 的索引，从第一个 '---' 之后开始搜索
        end_index = md_content.find('---', start_index + 3)
        # 找到了
        if end_index != -1:
            # 删除从第一个 '---' 到第二个 '---' 之间的内容
            md_content = md_content[:start_index] + md_content[end_index + 3:]

    return md_content
