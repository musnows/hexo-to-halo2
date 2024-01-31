# hexo-to-halo2

这是一个hexo博客批量上传并发布到halo2博客的脚本

> 测试环境：python3.10.5 和 halo v2.11.3

## 依赖项

下载python3.10.x（其余版本未测试是否可用），并安装依赖项

```
pip install -r requirements.txt
```

如果因为网络问题下载较慢，可以使用镜像源

```
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 配置

修改[config/config.exp.json](./config/config.exp.json)为`config/config.json`，并填充里面的内容

```json
{
    "userToken":"用户TOKEN",
    "haloSite":"站点链接",
    "published":true
}
```

说明：

* userToken字段：在halo2的个人中心中创建个人令牌，权限包括上传文章/发布文章和上传附件；
* haloSite字段：博客站点链接，不要带尾随斜杠。示例：`https://example.com`。错误写法为`https://example.com/`（这里错误地带了尾随斜杠）；
* published字段：用于配置是否发布文章，如果设置为true，则上传之后直接发布文章，如果设置为false则只上传、不发布。


## 使用

将markdown的md源文件放入文件夹，并复制文件夹路径。为了避免脚本处理出现异常，请将md源文件**复制一份**再调用本脚本。

```
python main.py 文件夹路径
```

脚本会自动遍历内部所有md文件，并根据md文件的front-matter进行解析和上传到halo。

> 初始版本没有实现图片上传逻辑，目前仅适用于md文件内的图片均为图床外链的情况。

我使用的是hexo-butterfly主题，md文件的front-matter示例如下。

```
---
title: 文章标题
tags:
  - 默认标签
categories:
  - 默认分组
cover: 封面图片链接
date: 创建时间
abbrlink: 永久链接
---
```

脚本会解析front-matter里面的内容，并同步到halo2站点中。

注意，abbrlink基于`hexo-abbrlink`插件，如果你的hexo博客没有安装此插件，front-matter中不会有该字段，这对上传脚本不影响。如果你的博客使用了该插件，脚本则会将abbrlink作为halo2内的`{slug}`进行上传，这样能保证hexo和halo2博客中文章链接一致，能实现无损迁移。

## 已知问题

halo2的文章发布时间字段暂时没有找到方法设置。

# 参考

halo2的API调用参考

* https://github.com/halo-sigs/vscode-extension-halo/blob/main/src/service/index.ts
* https://github.com/halo-dev/halo/issues/4936