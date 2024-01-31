import markdown


def render_markdown(content: str):
    """渲染md内容为html"""
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    html_content = markdown.markdown(content,extensions=exts)
    return html_content


def render_markdown_file(md_file_path: str):
    """渲染md文件为html"""
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return render_markdown(content)
