# Bilibili Crawler

一个用于爬取哔哩哔哩视频网站特定视频的评论和弹幕的Python脚本。

## 功能特性

- 爬取指定B站视频的弹幕数据
- 爬取指定B站视频的评论数据（包括子评论）
- 将数据保存为CSV格式文件

## 环境设置

### 自动设置（推荐）

运行自动设置脚本：
```bash
./setup.sh
```

### 手动设置

#### 创建虚拟环境

```bash
python3 -m venv venv
```

#### 激活虚拟环境

在 macOS/Linux 上:
```bash
source venv/bin/activate
```

在 Windows 上:
```bash
venv\Scripts\activate
```

#### 安装依赖

```bash
pip install -r requirements.txt
```

## VSCode终端问题解决

如果您在VSCode中遇到终端菜单栏内容都是灰色无法点击的问题，可以通过以下方式解决：

1. 确保已创建虚拟环境（如上一步所示）

2. 按 `Ctrl+Shift+P` 打开命令面板，输入 "Python: Select Interpreter" 并选择对应的Python解释器

3. 或者重启VSCode以使配置生效

4. 如果问题仍然存在，请检查 `.vscode/settings.json` 文件中的配置是否正确

## 使用方法

运行脚本:
```bash
python bilibili_crawler.py
```

然后根据提示输入B站视频链接或BV号（例如：`BV1xx411c7mu` 或 `https://www.bilibili.com/video/BV1xx411c7mu`）。

脚本会自动生成两个CSV文件：
1. `视频BV号_danmaku.csv` - 包含弹幕数据
2. `视频BV号_comments.csv` - 包含评论数据

## 配置说明

### 如何修改配置

如果需要修改配置，可以在运行脚本时通过以下方式：

1. 修改请求头信息：在 [bilibili_crawler.py](file:///Users/laplacetong/bilibili-crawler/bilibili_crawler.py) 文件中的 `__init__` 方法中修改 [headers](file:///Users/laplacetong/bilibili-crawler/bilibili_crawler.py#L21-L21) 参数。

2. 修改评论爬取数量：在调用 [crawl_comments](file:///Users/laplacetong/bilibili-crawler/bilibili_crawler.py#L110-L169) 方法时修改 `page_size` 参数。

3. 修改保存的文件名格式：修改 [save_danmaku_to_csv](file:///Users/laplacetong/bilibili-crawler/bilibili_crawler.py#L199-L222) 和 [save_comments_to_csv](file:///Users/laplacetong/bilibili-crawler/bilibili_crawler.py#L224-L247) 方法中的文件命名规则。

### 常见配置项

- **User-Agent**: 模拟浏览器请求，防止被反爬虫机制拦截
- **Referer**: 设置请求来源，B站可能对此有验证
- **延迟时间**: 在 [crawl_comments](file:///Users/laplacetong/bilibili-crawler/bilibili_crawler.py#L110-L169) 方法中设置，避免请求过于频繁

## 数据格式

### 弹幕数据

- `content`: 弹幕内容
- `time`: 弹幕出现时间（秒）
- `type`: 弹幕类型
- `fontsize`: 字体大小
- `color`: 颜色
- `timestamp`: 发送时间戳
- `pool`: 弹幕池
- `uid`: 发送者UID
- `row_id`: 弹幕ID

### 评论数据

- `rpid`: 评论ID
- `content`: 评论内容
- `ctime`: 创建时间
- `like`: 点赞数
- `member`: 用户名
- `mid`: 用户ID
- `level`: 用户等级
- `parent`: 父评论ID（仅子评论有）

## 注意事项

1. 请合理控制爬取频率，避免对B站服务器造成压力
2. B站API可能会有变化，如发现无法正常爬取，请检查API是否更新
3. 根据B站的robots.txt协议合理使用爬虫
4. 本工具仅供学习交流使用，请遵守相关法律法规