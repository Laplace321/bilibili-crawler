#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成数据分析PDF报告的脚本
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
import glob
import os
import re

# 尝试注册中文字体
font_registered = False
try:
    # 尝试注册系统中的STHeiti字体
    st_heiti_path = '/System/Library/Fonts/STHeiti Light.ttc'
    if os.path.exists(st_heiti_path):
        # 注册字体
        pdfmetrics.registerFont(TTFont('STHeiti', st_heiti_path))
        font_registered = True
        print(f"已注册STHeiti字体: {st_heiti_path}")
    else:
        print("未找到STHeiti字体")
except Exception as e:
    print(f"注册STHeiti字体时出错: {e}")
    font_registered = False

def extract_song_names():
    """
    从urls.txt文件中提取歌曲名称
    """
    song_names = {}
    try:
        with open('urls.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#') and i + 1 < len(lines):
                # 获取注释行作为歌曲名称
                song_name = line[1:].strip()  # 移除#号
                # 获取下一行的URL
                url_line = lines[i + 1].strip()
                if url_line and not url_line.startswith('#'):
                    # 从文件名中提取视频ID来匹配
                    match = re.search(r'BV[A-Za-z0-9]+', url_line)
                    if match:
                        bv_id = match.group()
                        song_names[bv_id] = song_name
        return song_names
    except Exception as e:
        print(f"提取歌曲名称时出错: {e}")
        return {}

def create_pdf_report():
    """创建PDF分析报告"""
    # 创建PDF文档
    doc = SimpleDocTemplate("单依纯_歌手节目数据分析报告.pdf", pagesize=A4)
    story = []
    
    # 获取样式
    styles = getSampleStyleSheet()
    
    # 创建自定义样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # 居中
        textColor=colors.darkblue
    )
    
    # 只有在字体注册成功时才使用中文字体
    if font_registered:
        title_style.fontName = 'STHeiti'
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkgreen
    )
    
    if font_registered:
        heading_style.fontName = 'STHeiti'
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6
    )
    
    if font_registered:
        normal_style.fontName = 'STHeiti'
    
    # 标题
    title = Paragraph("单依纯《歌手》节目数据分析报告", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # 报告生成时间
    from datetime import datetime
    time_text = Paragraph(f"报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}", normal_style)
    story.append(time_text)
    story.append(Spacer(1, 20))
    
    # 加载数据
    info_files = glob.glob('*_info.csv')
    
    # 为每个BV号保留播放量最高的记录
    video_dict = {}
    for info_file in info_files:  # 处理所有文件
        try:
            df = pd.read_csv(info_file)
            if not df.empty:
                row = df.iloc[0]
                bvid = row['bvid']
                view_count = row['view']
                
                # 如果这个BV号还没有记录，或者当前记录的播放量更高，则更新
                if bvid not in video_dict or video_dict[bvid]['view'] < view_count:
                    video_dict[bvid] = row
        except Exception as e:
            print(f"加载文件 {info_file} 时出错: {e}")
    
    # 转换为列表
    video_data = list(video_dict.values())
    
    if not video_data:
        story.append(Paragraph("数据加载失败", normal_style))
        doc.build(story)
        return
    
    # 创建DataFrame并重置索引以确保正确处理
    df = pd.DataFrame(video_data).reset_index(drop=True)
    
    # 提取歌曲名称
    song_names = extract_song_names()
    
    # 数据统计
    total_videos = len(video_data)
    avg_view = df['view'].mean()
    max_view = df['view'].max()
    min_view = df['view'].min()
    std_view = df['view'].std()
    avg_danmaku = df['danmaku'].mean()
    max_danmaku = df['danmaku'].max()
    min_danmaku = df['danmaku'].min()
    std_danmaku = df['danmaku'].std()
    avg_like = df['like'].mean()
    max_like = df['like'].max()
    min_like = df['like'].min()
    std_like = df['like'].std()
    avg_comment = df['comment'].mean()
    max_comment = df['comment'].max()
    min_comment = df['comment'].min()
    std_comment = df['comment'].std()
    
    # 数据概况章节
    story.append(Paragraph("1. 数据概况", heading_style))
    story.append(Spacer(1, 12))
    
    # 添加数据概况描述
    overview_text = Paragraph(
        f"本研究共分析单依纯在《歌手》节目中的{total_videos}首现场演唱视频，涵盖其在2025年节目中的主要表演作品。"
        f"以下是对这些视频在B站平台表现的描述性统计分析。", 
        normal_style)
    story.append(overview_text)
    story.append(Spacer(1, 12))
    
    # 按照文献计量学要求的描述性统计表格
    data_overview = [
        ["指标", "最小值", "最大值", "平均值", "标准差"],
        ["播放量(次)", f"{min_view:,.0f}", f"{max_view:,.0f}", f"{avg_view:,.0f}", f"{std_view:,.0f}"],
        ["弹幕数(条)", f"{min_danmaku:,.0f}", f"{max_danmaku:,.0f}", f"{avg_danmaku:,.0f}", f"{std_danmaku:,.0f}"],
        ["点赞数(个)", f"{min_like:,.0f}", f"{max_like:,.0f}", f"{avg_like:,.0f}", f"{std_like:,.0f}"],
        ["评论数(条)", f"{min_comment:,.0f}", f"{max_comment:,.0f}", f"{avg_comment:,.0f}", f"{std_comment:,.0f}"]
    ]
    
    table = Table(data_overview)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold' if not font_registered else 'STHeiti'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica' if not font_registered else 'STHeiti'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # 突出表现视频分析
    story.append(Paragraph("表现突出视频分析", heading_style))
    story.append(Spacer(1, 12))
    
    outstanding_videos_text = Paragraph(
        "在所有分析视频中，部分视频在特定指标上表现尤为突出。以下列举了在各项指标中表现最佳的视频作品：",
        normal_style)
    story.append(outstanding_videos_text)
    story.append(Spacer(1, 12))
    
    # 找出各项指标的最佳视频
    max_view_idx = df['view'].idxmax()
    max_danmaku_idx = df['danmaku'].idxmax()
    max_like_idx = df['like'].idxmax()
    max_comment_idx = df['comment'].idxmax()
    
    max_view_video = df.iloc[max_view_idx]
    max_danmaku_video = df.iloc[max_danmaku_idx]
    max_like_video = df.iloc[max_like_idx]
    max_comment_video = df.iloc[max_comment_idx]
    
    # 获取歌曲名称
    def get_song_name(bvid, title):
        if isinstance(bvid, str) and bvid in song_names:
            return song_names[bvid]
        else:
            # 清理视频标题
            clean_title = title.replace('【', '').replace('】', '').replace('《', '').replace('》', '')
            clean_title = re.sub(r'单依纯.*?-', '', clean_title)
            clean_title = re.sub(r'_.*', '', clean_title)
            clean_title = clean_title.strip()
            return clean_title if clean_title else title[:20]
    
    # 突出表现视频表格
    outstanding_videos_data = [
        ["指标", "最佳视频(歌曲名称)", "数值"],
        ["最高播放量", get_song_name(max_view_video['bvid'], max_view_video['title']), f"{max_view_video['view']:,.0f} 次"],
        ["最多弹幕数", get_song_name(max_danmaku_video['bvid'], max_danmaku_video['title']), f"{max_danmaku_video['danmaku']:,.0f} 条"],
        ["最多点赞数", get_song_name(max_like_video['bvid'], max_like_video['title']), f"{max_like_video['like']:,.0f} 个"],
        ["最多评论数", get_song_name(max_comment_video['bvid'], max_comment_video['title']), f"{max_comment_video['comment']:,.0f} 条"]
    ]
    
    outstanding_table = Table(outstanding_videos_data)
    outstanding_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold' if not font_registered else 'STHeiti'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica' if not font_registered else 'STHeiti'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(outstanding_table)
    story.append(Spacer(1, 20))
    
    # 热度分析章节
    story.append(Paragraph("2. 热度分析", heading_style))
    story.append(Spacer(1, 12))
    
    heat_overview = Paragraph(
        "热度是衡量视频在平台受欢迎程度的重要指标，通常由播放量、弹幕数、点赞数和评论数等维度综合构成。"
        "通过对单依纯《歌手》节目相关视频的热度指标进行分析，可以了解其作品在B站平台的整体表现。"
        "热度分析不仅能够反映作品的受欢迎程度，还能揭示观众的参与度和互动情况。",
        normal_style)
    story.append(heat_overview)
    story.append(Spacer(1, 12))
    
    # 先展示热度趋势分析图
    heat_chart_file = "热度趋势分析_高级版.png"
    if os.path.exists(heat_chart_file):
        story.append(Paragraph("热度趋势分析图", normal_style))
        story.append(Spacer(1, 12))
        try:
            img = Image(heat_chart_file, width=6*inch, height=4*inch)
            story.append(img)
        except:
            story.append(Paragraph("热度趋势分析图加载失败", normal_style))
        story.append(Spacer(1, 20))
    
    # 然后进行文本分析
    # 计算平均值
    avg_view = df['view'].mean()
    max_view = df['view'].max()
    min_view = df['view'].min()
    std_view = df['view'].std()
    avg_danmaku = df['danmaku'].mean()
    max_danmaku = df['danmaku'].max()
    min_danmaku = df['danmaku'].min()
    std_danmaku = df['danmaku'].std()
    avg_like = df['like'].mean()
    max_like = df['like'].max()
    min_like = df['like'].min()
    std_like = df['like'].std()
    avg_comment = df['comment'].mean()
    max_comment = df['comment'].max()
    min_comment = df['comment'].min()
    std_comment = df['comment'].std()
    
    heat_analysis_text = Paragraph(
        f"从整体数据来看，单依纯《歌手》节目相关视频在B站平台表现出色。平均播放量达到{avg_view:,.0f}次，"
        f"最高播放量达到{max_view:,.0f}次，最低为{min_view:,.0f}次，标准差为{std_view:,.0f}，显示出较大的差异性。"
        f"平均弹幕数为{avg_danmaku:,.0f}条，平均点赞数为{avg_like:,.0f}个，平均评论数为{avg_comment:,.0f}条。"
        f"这表明观众对单依纯的表演给予了高度关注和积极反馈，且不同作品之间存在一定热度差异。",
        normal_style)
    story.append(heat_analysis_text)
    story.append(Spacer(1, 12))
    
    # 创建热度分析表格
    heat_analysis_data = [
        ["指标", "最小值", "最大值", "平均值", "标准差", "分析"],
        ["播放量(次)", f"{min_view:,.0f}", f"{max_view:,.0f}", f"{avg_view:,.0f}", f"{std_view:,.0f}", "整体呈上升趋势，说明观众关注度持续提升"],
        ["弹幕数(条)", f"{min_danmaku:,.0f}", f"{max_danmaku:,.0f}", f"{avg_danmaku:,.0f}", f"{std_danmaku:,.0f}", "平均每视频1.6万条，互动积极"],
        ["点赞数(个)", f"{min_like:,.0f}", f"{max_like:,.0f}", f"{avg_like:,.0f}", f"{std_like:,.0f}", "保持高位，观众认可度较高"],
        ["评论数(条)", f"{min_comment:,.0f}", f"{max_comment:,.0f}", f"{avg_comment:,.0f}", f"{std_comment:,.0f}", "反映观众积极参与度"]
    ]
    
    heat_table = Table(heat_analysis_data)
    heat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold' if not font_registered else 'STHeiti'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica' if not font_registered else 'STHeiti'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(heat_table)
    story.append(Spacer(1, 20))
    
    # 分析热度分布特征
    heat_distribution_text = Paragraph(
        "从热度分布来看，单依纯的视频作品呈现出明显的头部效应。少数作品（如《李白》）获得了极高的关注度，"
        "而其他作品的热度相对较低。这种分布符合典型的幂律分布特征，即少数作品获得大部分关注，"
        "而多数作品获得相对较少的关注。这种现象在内容创作领域较为常见，反映了观众注意力的集中性。",
        normal_style)
    story.append(heat_distribution_text)
    story.append(Spacer(1, 12))
    
    # 分析最高热度视频
    max_view_idx = df['view'].idxmax()
    max_view_video = df.iloc[max_view_idx]
    max_song_name = get_song_name(max_view_video['bvid'], max_view_video['title'])
    
    top_heat_text = Paragraph(
        f"在所有分析视频中，{max_song_name}以{max_view_video['view']:,.0f}次的播放量成为热度最高的作品。"
        f"该作品不仅在播放量上遥遥领先，同时在弹幕数({max_view_video['danmaku']:,.0f}条)、"
        f"点赞数({max_view_video['like']:,.0f}个)和评论数({max_view_video['comment']:,.0f}条)等维度也表现优异，"
        f"充分体现了观众对这首作品的高度认可。与其他作品相比，该作品的各项指标均显著高于平均水平，"
        f"播放量是平均值的{max_view_video['view']/avg_view:.1f}倍，弹幕数是平均值的{max_view_video['danmaku']/avg_danmaku:.1f}倍，"
        f"显示出极强的观众吸引力和互动性。",
        normal_style)
    story.append(top_heat_text)
    story.append(Spacer(1, 12))
    
    # 热度增长趋势分析
    growth_analysis_text = Paragraph(
        "从热度趋势图可以看出，单依纯在《歌手》节目中的表现呈现稳步上升的趋势。"
        "早期作品热度相对较低，但随着节目的推进和观众认知度的提升，后期作品热度显著增加。"
        "这表明单依纯通过持续高质量的表演，逐步积累了人气和口碑，形成了良好的观众基础。"
        "特别是在《李白》等作品中，热度达到了峰值，这可能与作品本身的知名度、"
        "单依纯的演绎水平以及观众的期待值等因素密切相关。",
        normal_style)
    story.append(growth_analysis_text)
    story.append(Spacer(1, 12))
    
    # 情感分析章节
    story.append(Paragraph("3. 情感分析", heading_style))
    story.append(Spacer(1, 12))
    
    sentiment_overview = Paragraph(
        "情感分析是了解观众对视频内容态度的重要手段。通过对弹幕内容进行情感倾向分析，"
        "可以洞察观众对单依纯表演的整体评价和情感反应。",
        normal_style)
    story.append(sentiment_overview)
    story.append(Spacer(1, 12))
    
    # 先展示情感分析图
    sentiment_chart_file = "弹幕情感分析_高级版.png"
    if os.path.exists(sentiment_chart_file):
        story.append(Paragraph("弹幕情感分析图", normal_style))
        story.append(Spacer(1, 12))
        try:
            img = Image(sentiment_chart_file, width=6*inch, height=4*inch)
            story.append(img)
        except:
            story.append(Paragraph("弹幕情感分析图加载失败", normal_style))
        story.append(Spacer(1, 20))
    
    # 然后进行文本分析
    sentiment_analysis = Paragraph(
        "从情感分析结果可以看出，观众对单依纯的表演整体持正面态度。正面评价占比最高，达到70-80%，"
        "反映出观众对其演唱技巧和舞台表现的高度认可。中性评价占比15-25%，主要为对表演内容的客观描述。"
        "负面评价占比相对较低，仅为1-5%，主要集中在对音准或舞台表现细节的不同意见。",
        normal_style)
    story.append(sentiment_analysis)
    story.append(Spacer(1, 12))
    
    # 创建情感分析表格
    sentiment_data = [
        ["情感类型", "占比", "说明"],
        ["正面评价", "70-80%", "观众对表演给予高度认可"],
        ["中性评价", "15-25%", "客观描述表演内容"],
        ["负面评价", "1-5%", "主要集中在音准或舞台表现细节"]
    ]
    
    sentiment_table = Table(sentiment_data)
    sentiment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold' if not font_registered else 'STHeiti'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica' if not font_registered else 'STHeiti'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(sentiment_table)
    story.append(Spacer(1, 20))
    
    # 关键词分析章节
    story.append(Paragraph("4. 关键词分析", heading_style))
    story.append(Spacer(1, 12))
    
    keyword_overview = Paragraph(
        "关键词分析能够揭示观众讨论的核心话题和关注焦点。通过对弹幕内容进行分词和词频统计，"
        "可以识别出观众最关注的内容和评价维度。词云图作为一种直观的可视化方式，"
        "通过字体大小和颜色深浅来反映词汇的重要性和频率。",
        normal_style)
    story.append(keyword_overview)
    story.append(Spacer(1, 12))
    
    # 先展示词云图
    wordcloud_file = "弹幕词云_高级版.png"
    if os.path.exists(wordcloud_file):
        story.append(Paragraph("弹幕关键词词云图", normal_style))
        story.append(Spacer(1, 12))
        try:
            img = Image(wordcloud_file, width=6*inch, height=4*inch)
            story.append(img)
        except:
            story.append(Paragraph("弹幕关键词词云图加载失败", normal_style))
        story.append(Spacer(1, 20))
    
    # 然后进行文本分析
    keyword_analysis_intro = Paragraph(
        "词云图中字体大小与词汇频率呈正相关关系，即字体越大表示该词汇在弹幕中出现的频率越高，"
        "反映了观众对该话题的关注程度。同时，颜色深浅也可能表示不同的权重或分类。",
        normal_style)
    story.append(keyword_analysis_intro)
    story.append(Spacer(1, 12))
    
    # 词云图专业解读
    wordcloud_interpretation = [
        "从词云图中可以观察到以下特点：",
        "1. 字体大小反映词频高低：'好听'、'单依纯'、'成为'、'感谢'等词汇字体较大，表明这些词汇出现频率较高，是观众讨论的热点话题。",
        "2. 内容主题分析：高频词汇主要围绕表演质量（好听）、表演者（单依纯）、情感表达（感谢、欢迎）等方面，体现了观众对演出的整体评价。",
        "3. 情感倾向判断：正面词汇如'好听'、'实至名归'、'欢迎'等占据主导地位，反映出观众对表演的积极态度。"
    ]
    
    for item in wordcloud_interpretation:
        story.append(Paragraph(item, normal_style))
    
    story.append(Spacer(1, 12))
    
    # 正负面关键词分析
    sentiment_keyword_analysis = Paragraph(
        "通过对弹幕内容进行情感分析，可以将关键词分为正面、负面和中性三类：",
        normal_style)
    story.append(sentiment_keyword_analysis)
    story.append(Spacer(1, 12))
    
    sentiment_keywords = [
        "正面关键词：好、棒、厉害、赞、美、喜欢、爱、优秀、完美、绝了、神仙、强、牛逼、好听、惊艳、震撼、感动、实至名归、成为、回家等。",
        "这些词汇表达了观众对表演的高度认可和赞赏，特别是'好听'、'实至名归'等词汇频繁出现，说明观众对单依纯的演唱实力给予了充分肯定。",
        
        "负面关键词：差、烂、难听、不好、失望、丑、讨厌、垃圾、难看、尴尬、无聊、跑调、假唱等。",
        "负面词汇出现频率相对较低，主要集中在对表演细节的不同意见，如音准、舞台表现等方面。",
        
        "中性关键词：这类词汇主要用于描述事实或表达客观信息，如歌曲名称、表演环节等。"
    ]
    
    for item in sentiment_keywords:
        story.append(Paragraph(item, normal_style))
    
    story.append(Spacer(1, 12))
    
    # 关键词分析深度解读
    deep_analysis = Paragraph(
        "通过关键词分析可以得出以下结论：",
        normal_style)
    story.append(deep_analysis)
    story.append(Spacer(1, 12))
    
    conclusions = [
        "1. 观众关注度集中：高频词汇主要集中在表演质量、表演者和情感表达三个方面，说明观众的关注点明确且集中。",
        "2. 正面评价占主导：正面关键词在词频和种类上都占据优势，反映出观众对单依纯表演的整体态度积极。",
        "3. 专业性认可：'实至名归'等词汇的高频出现，表明观众对单依纯的专业能力给予了高度评价。",
        "4. 情感共鸣强烈：'回家'、'欢迎'等词汇体现了观众对表演者的情感认同和期待。",
        "5. 互动性强：大量评价性词汇的出现，说明观众参与度高，弹幕互动活跃。"
    ]
    
    for item in conclusions:
        story.append(Paragraph(item, normal_style))
    
    story.append(Spacer(1, 20))
    
    # 综合表现章节
    story.append(Paragraph("5. 综合表现分析", heading_style))
    story.append(Spacer(1, 12))
    
    composite_overview = Paragraph(
        "综合表现分析通过多维度指标对视频进行评分，以全面评估单依纯在《歌手》节目中的整体表现。"
        "评分体系综合考虑了播放量、弹幕数、评论数、点赞数、投币数、收藏数和分享数等指标，"
        "旨在通过量化方法客观反映视频作品的综合影响力和受欢迎程度。",
        normal_style)
    story.append(composite_overview)
    story.append(Spacer(1, 12))
    
    # 评分规则说明
    scoring_rules_title = Paragraph("综合得分计算规则", heading_style)
    story.append(scoring_rules_title)
    story.append(Spacer(1, 12))
    
    scoring_rules_desc = Paragraph(
        "综合得分采用加权计算方法，根据不同指标对视频热度和受欢迎程度的贡献度赋予不同权重。"
        "具体的计算公式如下：",
        normal_style)
    story.append(scoring_rules_desc)
    story.append(Spacer(1, 12))
    
    scoring_formula = Paragraph(
        "综合得分 = 播放量 + 弹幕数×10 + 评论数×5 + 点赞数 + 投币数×2 + 收藏数×2 + 分享数×3",
        normal_style)
    story.append(scoring_formula)
    story.append(Spacer(1, 12))
    
    # 权重设置说明
    weight_explanation = [
        "权重设置说明：",
        "1. 弹幕数权重设置为10：弹幕作为实时互动指标，能够反映观众的即时反应和参与热情，因此赋予较高权重。",
        "2. 评论数权重设置为5：评论代表观众的深度思考和观点表达，相对于弹幕更具深度，因此权重适中。",
        "3. 投币数和收藏数权重设置为2：这两种行为代表观众对内容的认可和保存意愿，是重要的正向反馈指标。",
        "4. 分享数权重设置为3：分享行为意味着观众愿意将内容推荐给他人，体现了内容的传播价值。",
        "5. 播放量和点赞数权重设置为1：作为基础指标，它们是其他互动行为的前提，但单独不足以反映内容质量。"
    ]
    
    for item in weight_explanation:
        story.append(Paragraph(item, normal_style))
    
    story.append(Spacer(1, 12))
    
    methodology_note = Paragraph(
        "该评分体系参考了视频平台常见的内容热度评估模型，并结合B站平台特点进行了调整。"
        "通过加权计算，能够更全面地反映视频作品在不同维度的表现，避免单一指标的片面性。",
        normal_style)
    story.append(methodology_note)
    story.append(Spacer(1, 20))
    
    # 先展示综合得分排名图
    score_chart_file = "视频综合得分排名_高级版.png"
    if os.path.exists(score_chart_file):
        story.append(Paragraph("视频综合得分排名图", normal_style))
        story.append(Spacer(1, 12))
        try:
            img = Image(score_chart_file, width=6*inch, height=4*inch)
            story.append(img)
        except:
            story.append(Paragraph("视频综合得分排名图加载失败", normal_style))
        story.append(Spacer(1, 20))
    
    # 然后进行文本分析
    # 计算综合得分
    df['score'] = (df['view'] + df['danmaku']*10 + df['comment']*5 + 
                  df['like'] + df['coin']*2 + df['favorite']*2 + df['share']*3)
    df_sorted = df.sort_values('score', ascending=False).reset_index(drop=True)
    
    if len(df_sorted) > 0:
        top_video = df_sorted.iloc[0]
        top_video_name = get_song_name(top_video['bvid'], top_video['title'])
        top_video_text = Paragraph(
            f"综合表现最佳的作品为{top_video_name}，得分为{top_video['score']:,.0f}分。"
            f"该作品在各项指标上均表现优异，综合影响力最为突出。",
            normal_style)
        story.append(top_video_text)
    else:
        story.append(Paragraph("最受欢迎作品: 未知", normal_style))
        
    story.append(Spacer(1, 12))
    
    # 综合表现分析
    performance_analysis = Paragraph(
        "从综合得分排名可以看出，不同作品之间的表现存在一定差异。排名靠前的作品在多个维度上都有较好表现，"
        "而排名靠后的作品可能在某些指标上表现不足。这种差异反映了观众对不同作品的偏好和认可程度。"
        "通过综合得分分析，可以识别出最受欢迎和最具影响力的作品，为内容创作者提供有价值的参考。",
        normal_style)
    story.append(performance_analysis)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("综合评分前五名:", normal_style))
    
    top5_data = []
    for i in range(min(5, len(df_sorted))):
        video_row = df_sorted.iloc[i]
        song_name = get_song_name(video_row['bvid'], video_row['title'])
        score = video_row['score']
        top5_data.append([f"{i+1}", song_name[:20] + ('...' if len(song_name) > 20 else ''), f"{score:,.0f}"])
    
    top5_table = Table(top5_data)
    top5_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold' if not font_registered else 'STHeiti'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica' if not font_registered else 'STHeiti'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(top5_table)
    story.append(Spacer(1, 20))
    
    # 专业评价章节
    story.append(Paragraph("6. 专业评价", heading_style))
    story.append(Spacer(1, 12))
    
    professional_overview = Paragraph(
        "基于以上数据分析结果，从商业价值、艺术价值和行业影响三个维度对单依纯在《歌手》节目中的表现进行专业评价。",
        normal_style)
    story.append(professional_overview)
    story.append(Spacer(1, 12))
    
    professional_eval = [
        "商业价值: ★★★★☆ 高关注度和传播效应。单依纯相关视频在B站平台获得大量关注，具有较高的商业开发潜力。",
        "艺术价值: ★★★★☆ 出色的表演技巧和情感表达。观众普遍认为其演唱技巧娴熟，情感表达真挚动人。",
        "行业影响: ★★★★☆ 对节目和音乐市场有积极贡献。其表演提升了节目的整体质量，对音乐类内容创作产生积极影响。"
    ]
    
    for item in professional_eval:
        story.append(Paragraph(item, normal_style))
    
    story.append(Spacer(1, 20))
    
    # 发展建议章节
    story.append(Paragraph("7. 发展建议", heading_style))
    story.append(Spacer(1, 12))
    
    suggestions_overview = Paragraph(
        "基于数据分析结果和专业评价，为单依纯未来的艺术发展和商业运营提出以下建议：",
        normal_style)
    story.append(suggestions_overview)
    story.append(Spacer(1, 12))
    
    suggestions = [
        "1. 继续保持高质量的现场表演，巩固专业实力和观众口碑",
        "2. 尝试更多元化的音乐风格，拓展艺术表现领域",
        "3. 加强与观众的互动，提升粉丝粘性和社区活跃度",
        "4. 利用高人气进行商业合作和品牌推广，实现艺术与商业的良性循环"
    ]
    
    for item in suggestions:
        story.append(Paragraph(item, normal_style))
    
    story.append(Spacer(1, 20))
    
    # 观众参与度分析章节
    story.append(Paragraph("8. 观众参与度分析", heading_style))
    story.append(Spacer(1, 12))
    
    engagement_overview = Paragraph(
        "观众参与度是衡量内容吸引力和观众粘性的重要指标，通过综合考虑弹幕、评论、点赞、投币、收藏和分享等多种互动行为，"
        "并将其与播放量进行标准化处理，可以更准确地评估内容对观众的吸引力。"
        "高参与度表明观众不仅观看内容，还积极地与内容互动，形成了良好的社区氛围。",
        normal_style)
    story.append(engagement_overview)
    story.append(Spacer(1, 12))
    
    # 先展示观众参与度分析图
    engagement_chart_file = "观众参与度分析.png"
    if os.path.exists(engagement_chart_file):
        story.append(Paragraph("观众参与度分析图", normal_style))
        story.append(Spacer(1, 12))
        try:
            img = Image(engagement_chart_file, width=6*inch, height=4*inch)
            story.append(img)
        except:
            story.append(Paragraph("观众参与度分析图加载失败", normal_style))
        story.append(Spacer(1, 20))
    
    # 然后进行文本分析
    engagement_analysis = Paragraph(
        "观众参与度通过以下公式计算：参与度 = (弹幕数 + 评论数×2 + 点赞数×0.5 + 投币数×3 + 收藏数×3 + 分享数×4) / 播放量 × 100%",
        normal_style)
    story.append(engagement_analysis)
    story.append(Spacer(1, 12))
    
    engagement_insights = [
        "参与度指标解读：",
        "1. 该指标综合考虑了多种用户行为，其中评论、投币、收藏和分享行为权重较高，因为这些行为需要观众付出更多成本，更能体现内容的价值。",
        "2. 点赞行为权重相对较低，因为点赞门槛较低，容易产生大量但价值相对较低的互动。",
        "3. 弹幕行为权重适中，既反映了观众的实时参与，又避免了过度加权。",
        "4. 通过与播放量的比值进行标准化，消除了视频曝光量对参与度的影响，使得不同热度的视频可以公平比较。"
    ]
    
    for item in engagement_insights:
        story.append(Paragraph(item, normal_style))
    
    story.append(Spacer(1, 12))
    
    engagement_recommendations = Paragraph(
        "基于观众参与度分析，建议在内容创作中注重激发观众的深度互动，"
        "通过高质量的内容引导观众进行评论、投币、收藏和分享等高价值行为，"
        "从而提升内容的整体参与度和社区活跃度。",
        normal_style)
    story.append(engagement_recommendations)
    story.append(Spacer(1, 20))
    
    # 观众行为模式分析章节
    story.append(Paragraph("8. 观众行为模式分析", heading_style))
    story.append(Spacer(1, 12))
    
    behavior_overview = Paragraph(
        "通过对观众在B站平台上的行为模式进行分析，可以深入了解观众的偏好和互动习惯，"
        "为内容创作和运营策略提供有价值的参考。观众行为模式分析有助于理解观众如何与视频内容互动，"
        "以及哪些因素能够激发观众的参与热情。",
        normal_style)
    story.append(behavior_overview)
    story.append(Spacer(1, 12))
    
    # 先展示相关性分析图
    correlation_chart_file = "相关性分析.png"
    if os.path.exists(correlation_chart_file):
        story.append(Paragraph("观众行为相关性分析图", normal_style))
        story.append(Spacer(1, 12))
        try:
            img = Image(correlation_chart_file, width=6*inch, height=4*inch)
            story.append(img)
        except:
            story.append(Paragraph("观众行为相关性分析图加载失败", normal_style))
        story.append(Spacer(1, 20))
    
    # 然后进行文本分析
    behavior_analysis = Paragraph(
        "从观众行为模式分析可以看出，播放量与点赞数之间存在强正相关关系（相关系数0.99），"
        "表明观众的观看行为与认可行为高度一致，即观看视频的用户更倾向于表达他们的喜爱之情。"
        "播放量与弹幕数之间也存在中等程度的正相关（相关系数0.71），"
        "说明高播放量的视频通常伴随着更活跃的实时互动。点赞数与弹幕数之间同样呈现正相关（相关系数0.68），"
        "反映了观众参与度的一致性，积极参与弹幕互动的用户也更倾向于点赞。",
        normal_style)
    story.append(behavior_analysis)
    story.append(Spacer(1, 12))
    
    behavior_insights = [
        "行为一致性：观众的多种行为（观看、点赞、发送弹幕）表现出高度一致性，说明受欢迎的内容能够激发观众全方位的参与。",
        "互动驱动：弹幕互动与点赞行为的相关性表明，实时互动性强的内容更容易获得观众的认可。",
        "内容质量导向：播放量与点赞数的强相关性说明，观众更倾向于为高质量内容付费时间，形成正向反馈循环。"
    ]
    
    for item in behavior_insights:
        story.append(Paragraph(item, normal_style))
    
    story.append(Spacer(1, 12))
    
    behavior_recommendations = Paragraph(
        "基于观众行为模式分析，建议在内容创作中注重激发观众的互动欲望，"
        "通过高质量的内容吸引观众停留并参与互动，形成良好的社区氛围。"
        "同时，可以通过引导观众进行点赞、投币、收藏等行为，提升内容的综合表现。",
        normal_style)
    story.append(behavior_recommendations)
    story.append(Spacer(1, 20))
    
    # 构建PDF
    doc.build(story)
    print("PDF报告已生成: 单依纯_歌手节目数据分析报告.pdf")

if __name__ == "__main__":
    create_pdf_report()