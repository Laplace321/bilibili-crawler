# Bilibili Crawler - 单依纯《歌手》节目数据分析项目

![GitHub](https://img.shields.io/github/license/yourusername/bilibili-crawler)
![GitHub top language](https://img.shields.io/github/languages/top/yourusername/bilibili-crawler)
![GitHub repo size](https://img.shields.io/github/repo-size/yourusername/bilibili-crawler)

## 项目概述

本项目是一个针对 Bilibili 视频平台的数据爬取和分析工具，专门用于分析单依纯在2025年《歌手》节目中13首现场演唱视频的数据。通过热度趋势、弹幕情感、关键词分析和综合评分等维度，全面评估其在节目中的表现。

## 功能特点

- **数据爬取**: 自动从 Bilibili 平台获取视频数据，包括播放量、弹幕、评论、点赞等
- **数据分析**: 对获取的数据进行多维度分析，包括：
  - 热度趋势分析
  - 弹幕情感分析
  - 关键词分析
  - 综合评分排名
- **可视化展示**: 生成图表直观展示分析结果
- **报告生成**: 自动生成 PDF 和 PPT 格式的分析报告

## 项目结构

```
.
├── bilibili_crawler.py          # Bilibili数据爬取主程序
├── advanced_analyze_data.py     # 高级数据分析程序
├── generate_pdf_report.py       # PDF报告生成程序
├── convert_pdf_to_ppt.py        # PDF转PPT程序
├── urls.txt                     # 待分析视频链接列表
├── requirements.txt             # 项目依赖列表
├── setup.sh                     # 环境设置脚本
├── 数据分析报告.md              # Markdown格式分析报告
├── 单依纯_歌手节目数据分析报告.pdf  # PDF格式分析报告
└── 单依纯_歌手节目数据分析报告_带图表.pptx  # PPT格式分析报告
```

## 功能特点

### 数据爬取
- 支持批量抓取B站视频信息和弹幕数据
- 自动处理反爬虫机制
- 支持通过cookies进行登录状态模拟

### 数据分析
- 热度趋势分析
- 弹幕情感分析
- 关键词提取与词云生成
- 观众参与度分析
- 综合评分系统

### 可视化展示
- 热度趋势图表
- 弹幕情感分布图
- 关键词词云图
- 综合得分排名图
- 观众参与度分析图

### 报告生成
- 自动生成PDF格式分析报告
- 生成带解说备注的PPT演示文稿
- 专业的报告结构和内容组织

## 安装与使用

### 环境要求

- Python 3.6+
- pip 包管理器

### 安装步骤

1. 克隆项目到本地：
```bash
git clone https://github.com/yourusername/bilibili-crawler.git
cd bilibili-crawler
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

### 使用方法

1. 在 `urls.txt` 文件中添加需要分析的视频链接
2. 运行爬虫程序获取数据：
```bash
python bilibili_crawler.py
```
3. 运行数据分析程序：
```bash
python advanced_analyze_data.py
```
4. 生成PDF报告：
```bash
python generate_pdf_report.py
```
5. 转换为PPT报告：
```bash
python convert_pdf_to_ppt.py
```


## 技术栈

- Python 3
- requests - 网络请求库
- pandas - 数据分析库
- matplotlib - 数据可视化库
- seaborn - 高级数据可视化库
- wordcloud - 词云生成库
- reportlab - PDF报告生成库
- python-pptx - PPT生成库

## 分析维度

### 1. 数据概况
- 分析视频数量
- 平均播放量、弹幕数、点赞数、评论数等基础数据

### 2. 热度趋势分析
- 各项指标随时间的变化趋势
- 不同作品的表现对比

### 3. 弹幕情感分析
- 正面、负面、中性评价的分布
- 典型正面和负面关键词分析

### 4. 关键词分析
- 高频词汇提取和词云展示
- 观众关注点分析

### 5. 综合评分排名
- 基于多维度指标的综合评分
- 各作品排名对比

### 6. 专业评价
- 商业价值评估
- 艺术价值分析
- 行业影响评价

## 生成报告示例

### PDF报告
[![PDF报告](https://img.shields.io/badge/查看-PDF报告-blue)](单依纯_歌手节目数据分析报告.pdf)

### PPT报告
[![PPT报告](https://img.shields.io/badge/查看-PPT报告-orange)](单依纯_歌手节目数据分析报告_带图表.pptx)

## 注意事项

1. 本项目仅供学习交流使用，请遵守相关法律法规和平台使用条款
2. 请合理控制爬取频率，避免对平台服务器造成压力
3. 爬取的数据仅用于个人学习分析，不得用于商业用途

## 许可证

本项目采用 MIT 许可证，详情请见 [LICENSE](LICENSE) 文件。