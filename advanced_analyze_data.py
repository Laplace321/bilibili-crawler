#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单依纯《歌手》节目高级数据分析脚本
功能：使用更高级的可视化技术分析单依纯在2025年《歌手》节目中14首现场演唱视频的数据
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import jieba
from wordcloud import WordCloud
from collections import Counter
import re
import os
import glob
import warnings
warnings.filterwarnings('ignore')

# 尝试设置中文字体
def set_chinese_font():
    """
    设置中文字体以确保正确显示中文，优先使用苹方字体
    """
    # 查找可用的中文字体
    all_fonts = fm.fontManager.ttflist
    
    # 优先查找苹方字体
    pingfang_fonts = [f for f in all_fonts if 'PingFang' in f.name]
    
    # 查找其他中文字体
    chinese_fonts = [f for f in all_fonts if 
                    any(key in f.name.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'pmingliu', 'hei', 'song', 'kai']) or
                    any(key in f.fname.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'pmingliu', 'hei', 'song', 'kai'])]
    
    if pingfang_fonts:
        # 使用苹方字体
        font_names = [f.name for f in pingfang_fonts[:3]]
        plt.rcParams['font.sans-serif'] = font_names + ['sans-serif']
        print(f"使用苹方字体: {font_names[0] if font_names else '未知'}")
        return pingfang_fonts
    elif chinese_fonts:
        # 使用其他中文字体
        font_names = [f.name for f in chinese_fonts[:5]]
        plt.rcParams['font.sans-serif'] = font_names + ['sans-serif']
        print(f"使用中文字体: {font_names[0] if font_names else '未知'}")
        return chinese_fonts
    else:
        # 备选方案：使用系统默认字体并尝试支持中文
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
        print("使用备选字体方案")
        return []

# 设置中文字体
chinese_fonts = set_chinese_font()

# 创建全局字体属性对象
def create_font_properties():
    """
    创建字体属性对象
    """
    # 查找苹方字体
    pingfang_fonts = [f for f in fm.fontManager.ttflist if 'PingFang' in f.name]
    
    if pingfang_fonts:
        font_name = pingfang_fonts[0].name
        font_path = pingfang_fonts[0].fname
        try:
            # 创建字体属性对象
            chinese_font_prop = fm.FontProperties(fname=font_path)
            title_font_prop = fm.FontProperties(fname=font_path, size=14, weight='bold')
            label_font_prop = fm.FontProperties(fname=font_path, size=12)
            big_title_font_prop = fm.FontProperties(fname=font_path, size=16, weight='bold')
            print(f"创建字体属性对象: {font_name}")
            return chinese_font_prop, title_font_prop, label_font_prop, big_title_font_prop
        except Exception as e:
            print(f"创建字体属性对象失败: {e}")
    
    # 如果无法创建苹方字体属性，使用默认设置
    chinese_font_prop = None
    title_font_prop = None
    label_font_prop = None
    big_title_font_prop = None
    return chinese_font_prop, title_font_prop, label_font_prop, big_title_font_prop

chinese_font_prop, title_font_prop, label_font_prop, big_title_font_prop = create_font_properties()

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
        print(f"提取到 {len(song_names)} 个歌曲名称")
        return song_names
    except Exception as e:
        print(f"提取歌曲名称时出错: {e}")
        return {}

class AdvancedSingerDataAnalyzer:
    def __init__(self):
        self.video_data = []
        self.danmaku_data = []
        self.video_titles = []
        self.song_names = extract_song_names()  # 提取歌曲名称
        self.video_bvids = []  # 存储每个视频的BV号
        
    def load_data(self):
        """加载所有视频信息和弹幕数据"""
        # 查找所有info.csv文件
        info_files = glob.glob('*_info.csv')
        
        # 过滤掉旧格式的文件（包含特殊字符的文件）
        filtered_info_files = [f for f in info_files if not any(c in f for c in ['【', '《', '__'])]
        
        print(f"找到 {len(info_files)} 个视频信息文件，过滤后剩余 {len(filtered_info_files)} 个")
        
        # 加载视频信息数据
        for info_file in filtered_info_files:
            try:
                df = pd.read_csv(info_file)
                if not df.empty:
                    self.video_data.append(df.iloc[0])
                    # 存储视频的BV号
                    self.video_bvids.append(df.iloc[0]['bvid'])
                    
                    # 获取对应的弹幕文件名
                    danmaku_file = info_file.replace('_info.csv', '_danmaku.csv')
                    if os.path.exists(danmaku_file):
                        danmaku_df = pd.read_csv(danmaku_file)
                        # 为弹幕数据添加bvid列
                        danmaku_df['bvid'] = df.iloc[0]['bvid']
                        self.danmaku_data.append(danmaku_df)
                        
                        # 获取视频标题并尝试匹配歌曲名称
                        video_title = df.iloc[0]['title']
                        song_name = self.get_song_name(video_title, info_file)
                        self.video_titles.append(song_name)
                    else:
                        print(f"未找到弹幕文件: {danmaku_file}")
                        self.danmaku_data.append(pd.DataFrame())
                        video_title = df.iloc[0]['title']
                        song_name = self.get_song_name(video_title, info_file)
                        self.video_titles.append(song_name)
            except Exception as e:
                print(f"加载文件 {info_file} 时出错: {e}")
        
        print(f"成功加载 {len(self.video_data)} 个视频的数据")
        
    def get_song_name(self, video_title, file_path):
        """
        获取歌曲名称
        """
        # 首先尝试从urls.txt中获取
        match = re.search(r'BV[A-Za-z0-9]+', file_path)
        if match:
            bv_id = match.group()
            if bv_id in self.song_names:
                return self.song_names[bv_id]
        
        # 如果无法从urls.txt获取，则从视频标题中提取
        # 移除常见的前缀和后缀
        clean_title = video_title.replace('【', '').replace('】', '').replace('《', '').replace('》', '')
        clean_title = re.sub(r'单依纯.*?-', '', clean_title)  # 移除"单依纯"前缀
        clean_title = re.sub(r'_.*', '', clean_title)  # 移除下划线后的内容
        clean_title = clean_title.strip()
        
        # 如果标题太长，只取前20个字符
        if len(clean_title) > 20:
            clean_title = clean_title[:20] + '...'
            
        return clean_title if clean_title else video_title[:20]
        
    def analyze_heat_trend(self):
        """分析热度变化趋势"""
        if not self.video_data:
            print("没有数据可供分析")
            return
            
        # 创建DataFrame
        df = pd.DataFrame(self.video_data)
        
        # 按播放量排序（模拟时间顺序）
        df_sorted = df.sort_values('view', ascending=True).reset_index(drop=True)
        
        # 使用Seaborn创建更美观的图表
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('单依纯《歌手》节目热度趋势分析', fontsize=20, fontweight='bold', y=0.95, fontproperties=big_title_font_prop)
        
        # 获取排序后的歌曲名称
        sorted_song_names = []
        for _, row in df_sorted.iterrows():
            # 从视频标题中提取BV号来匹配歌曲名称
            match = re.search(r'BV[A-Za-z0-9]+', row['bvid'])
            if match and match.group() in self.song_names:
                song_name = self.song_names[match.group()]
            else:
                # 如果无法匹配，则使用清理后的标题
                clean_title = row['title'].replace('【', '').replace('】', '').replace('《', '').replace('》', '')
                clean_title = re.sub(r'单依纯.*?-', '', clean_title)
                clean_title = re.sub(r'_.*', '', clean_title)
                clean_title = clean_title.strip()
                song_name = clean_title if clean_title else row['title'][:20]
                # 如果标题太长，只取前10个字符
                if len(song_name) > 10:
                    song_name = song_name[:10] + '...'
            sorted_song_names.append(song_name)
        
        # 播放量趋势
        sns.lineplot(x=range(len(df_sorted)), y='view', data=df_sorted, marker='o', 
                    linewidth=2.5, markersize=10, ax=axes[0, 0], color='#1f77b4')
        axes[0, 0].set_title('播放量趋势', fontsize=16, pad=15, fontproperties=title_font_prop)
        axes[0, 0].set_xlabel('歌曲名称', fontsize=12, fontproperties=label_font_prop)
        axes[0, 0].set_ylabel('播放量', fontsize=12, fontproperties=label_font_prop)
        axes[0, 0].set_xticks(range(len(sorted_song_names)))
        axes[0, 0].set_xticklabels(sorted_song_names, rotation=45, ha='right', fontsize=10, fontproperties=chinese_font_prop)
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].ticklabel_format(style='plain', axis='y')
        
        # 弹幕数趋势
        sns.lineplot(x=range(len(df_sorted)), y='danmaku', data=df_sorted, marker='s', 
                    linewidth=2.5, markersize=10, ax=axes[0, 1], color='#ff7f0e')
        axes[0, 1].set_title('弹幕数趋势', fontsize=16, pad=15, fontproperties=title_font_prop)
        axes[0, 1].set_xlabel('歌曲名称', fontsize=12, fontproperties=label_font_prop)
        axes[0, 1].set_ylabel('弹幕数', fontsize=12, fontproperties=label_font_prop)
        axes[0, 1].set_xticks(range(len(sorted_song_names)))
        axes[0, 1].set_xticklabels(sorted_song_names, rotation=45, ha='right', fontsize=10, fontproperties=chinese_font_prop)
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].ticklabel_format(style='plain', axis='y')
        
        # 点赞数趋势
        sns.lineplot(x=range(len(df_sorted)), y='like', data=df_sorted, marker='^', 
                    linewidth=2.5, markersize=10, ax=axes[1, 0], color='#2ca02c')
        axes[1, 0].set_title('点赞数趋势', fontsize=16, pad=15, fontproperties=title_font_prop)
        axes[1, 0].set_xlabel('歌曲名称', fontsize=12, fontproperties=label_font_prop)
        axes[1, 0].set_ylabel('点赞数', fontsize=12, fontproperties=label_font_prop)
        axes[1, 0].set_xticks(range(len(sorted_song_names)))
        axes[1, 0].set_xticklabels(sorted_song_names, rotation=45, ha='right', fontsize=10, fontproperties=chinese_font_prop)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].ticklabel_format(style='plain', axis='y')
        
        # 评论数趋势
        sns.lineplot(x=range(len(df_sorted)), y='comment', data=df_sorted, marker='d', 
                    linewidth=2.5, markersize=10, ax=axes[1, 1], color='#d62728')
        axes[1, 1].set_title('评论数趋势', fontsize=16, pad=15, fontproperties=title_font_prop)
        axes[1, 1].set_xlabel('歌曲名称', fontsize=12, fontproperties=label_font_prop)
        axes[1, 1].set_ylabel('评论数', fontsize=12, fontproperties=label_font_prop)
        axes[1, 1].set_xticks(range(len(sorted_song_names)))
        axes[1, 1].set_xticklabels(sorted_song_names, rotation=45, ha='right', fontsize=10, fontproperties=chinese_font_prop)
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].ticklabel_format(style='plain', axis='y')
        
        plt.tight_layout()
        plt.savefig('热度趋势分析_高级版.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.show()
        
        # 输出统计信息
        print("\n=== 热度趋势分析 ===")
        print(f"平均播放量: {df['view'].mean():,.0f}")
        print(f"最高播放量: {df['view'].max():,.0f}")
        print(f"最低播放量: {df['view'].min():,.0f}")
        print(f"平均弹幕数: {df['danmaku'].mean():,.0f}")
        print(f"最高弹幕数: {df['danmaku'].max():,.0f}")
        print(f"最低弹幕数: {df['danmaku'].min():,.0f}")
        
    def analyze_danmaku_sentiment(self):
        """分析弹幕情感倾向"""
        if not self.danmaku_data:
            print("没有弹幕数据可供分析")
            return
            
        print("\n=== 弹幕情感分析 ===")
        
        # 简单的情感分析（基于关键词）
        positive_words = ['好', '棒', '厉害', '牛', '赞', '美', '喜欢', '爱', '优秀', '完美', '绝了', '神仙', '强', '牛逼', '太棒了', '好听', '惊艳', '震撼', '感动', '泪目', '实至名归', '成为', '回家', '厉害了', '精彩', '佩服', '鼓掌']
        negative_words = ['差', '烂', '难听', '不好', '失望', '丑', '讨厌', '垃圾', '难看', '尴尬', '无聊', '一般', '凑数', '不行', '难听', '跑调', '假唱']
        
        sentiment_results = []
        
        for i, danmaku_df in enumerate(self.danmaku_data):
            if danmaku_df.empty:
                sentiment_results.append({'positive': 0, 'negative': 0, 'neutral': 0})
                continue
                
            positive_count = 0
            negative_count = 0
            
            for content in danmaku_df['content'].fillna('').astype(str):
                # 简单的关键词匹配
                content_lower = content.lower()
                is_positive = any(word in content_lower for word in positive_words)
                is_negative = any(word in content_lower for word in negative_words)
                
                if is_positive and not is_negative:
                    positive_count += 1
                elif is_negative and not is_positive:
                    negative_count += 1
            
            neutral_count = len(danmaku_df) - positive_count - negative_count
            sentiment_results.append({
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            })
            
            print(f"{self.video_titles[i]}: 正面({positive_count}) 负面({negative_count}) 中性({neutral_count})")
        
        # 使用Seaborn绘制情感分析结果
        fig, ax = plt.subplots(figsize=(18, 10))
        
        # 准备数据
        n_videos = len(self.video_titles)
        x = np.arange(n_videos)
        width = 0.25
        
        # 获取用于图表显示的歌曲名称
        chart_song_names = []
        for i in range(n_videos):
            # 从视频BV号匹配歌曲名称
            if i < len(self.video_bvids) and self.video_bvids[i] in self.song_names:
                chart_song_names.append(self.song_names[self.video_bvids[i]])
            else:
                chart_song_names.append(self.video_titles[i][:10] + ('...' if len(self.video_titles[i]) > 10 else ''))
        
        positive_counts = [r['positive'] for r in sentiment_results]
        negative_counts = [r['negative'] for r in sentiment_results]
        neutral_counts = [r['neutral'] for r in sentiment_results]
        
        # 绘制堆叠柱状图
        p1 = ax.bar(x, positive_counts, width, label='正面', color='#28a745', alpha=0.8)
        p2 = ax.bar(x, negative_counts, width, bottom=positive_counts, label='负面', color='#dc3545', alpha=0.8)
        p3 = ax.bar(x, neutral_counts, width, bottom=np.array(positive_counts)+np.array(negative_counts), 
                   label='中性', color='#6c757d', alpha=0.8)
        
        # 添加数值标签
        for i in range(n_videos):
            # 正面标签
            ax.text(i, positive_counts[i]/2, str(positive_counts[i]), 
                   ha='center', va='center', fontsize=8, color='white', fontweight='bold')
            # 负面标签
            if negative_counts[i] > 0:
                ax.text(i, positive_counts[i] + negative_counts[i]/2, str(negative_counts[i]), 
                       ha='center', va='center', fontsize=8, color='white', fontweight='bold')
            # 中性标签
            if neutral_counts[i] > 0:
                ax.text(i, positive_counts[i] + negative_counts[i] + neutral_counts[i]/2, str(neutral_counts[i]), 
                       ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        
        ax.set_xlabel('视频作品', fontsize=14, fontproperties=label_font_prop)
        ax.set_ylabel('弹幕数量', fontsize=14, fontproperties=label_font_prop)
        ax.set_title('各视频弹幕情感倾向分析（堆叠柱状图）', fontsize=18, fontweight='bold', pad=20, fontproperties=big_title_font_prop)
        ax.set_xticks(x)
        ax.set_xticklabels(chart_song_names, rotation=45, ha='right', fontsize=10, fontproperties=chinese_font_prop)
        ax.legend(fontsize=12, loc='upper left')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('弹幕情感分析_高级版.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.show()
        
    def extract_keywords(self):
        """提取关键词并生成词云"""
        if not self.danmaku_data:
            print("没有弹幕数据可供分析")
            return
            
        print("\n=== 关键词分析 ===")
        
        # 合并所有弹幕
        all_contents = []
        for danmaku_df in self.danmaku_data:
            if not danmaku_df.empty:
                all_contents.extend(danmaku_df['content'].fillna('').astype(str).tolist())
        
        # 文本预处理
        text = ' '.join(all_contents)
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        
        # 中文分词
        words = jieba.lcut(text)
        
        # 过滤停用词和单字符
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '里', '就是', '还是', '为了', '只有', '时候', '已经', '可以', '什么', '怎么', '可能', '应该', '但是', '因为', '所以', '如果', '还是', '然后', '这个', '那个', '这些', '那些', '我们', '他们', '她们', '它们', '自己', '出来', '单依纯', '歌手', '舞台', '表演', '演唱', '现场', '节目'}
        filtered_words = [word for word in words if len(word) > 1 and word not in stopwords]
        
        # 统计词频
        word_freq = Counter(filtered_words)
        top_words = word_freq.most_common(100)
        
        print("高频词汇:")
        for word, freq in top_words[:10]:
            print(f"{word}: {freq}")
        
        # 生成词云
        try:
            # 创建一个更大的画布
            plt.figure(figsize=(14, 10))
            
            # 尝试使用系统字体生成词云
            # 查找可用的中文字体路径
            font_path = None
            # 优先查找苹方字体
            pingfang_fonts = [f for f in fm.fontManager.ttflist if 'PingFang' in f.name]
            if pingfang_fonts:
                font_path = pingfang_fonts[0].fname
            else:
                # 查找其他中文字体
                chinese_fonts = [f for f in fm.fontManager.ttflist if 
                                any(key in f.name.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'pmingliu', 'hei', 'song', 'kai'])]
                if chinese_fonts:
                    font_path = chinese_fonts[0].fname
            
            wordcloud = WordCloud(
                font_path=font_path,  # 明确指定字体路径
                width=1400, 
                height=1000, 
                background_color='white',
                max_words=150,
                colormap='plasma',
                relative_scaling=0.5,
                random_state=42,
                collocations=False
            ).generate_from_frequencies(dict(top_words))
            
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('弹幕关键词词云', fontsize=26, fontweight='bold', pad=20, fontproperties=big_title_font_prop)
            plt.tight_layout()
            plt.savefig('弹幕词云_高级版.png', dpi=300, bbox_inches='tight', facecolor='white')
            plt.show()
        except Exception as e:
            print(f"生成词云时出错: {e}")
            # 备选方案：尝试不指定字体路径
            try:
                plt.figure(figsize=(14, 10))
                wordcloud = WordCloud(
                    font_path=None,
                    width=1400, 
                    height=1000, 
                    background_color='white',
                    max_words=150,
                    colormap='plasma',
                    relative_scaling=0.5,
                    random_state=42,
                    collocations=False
                ).generate_from_frequencies(dict(top_words))
                
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title('弹幕关键词词云', fontsize=26, fontweight='bold', pad=20, fontproperties=big_title_font_prop)
                plt.tight_layout()
                plt.savefig('弹幕词云_高级版.png', dpi=300, bbox_inches='tight', facecolor='white')
                plt.show()
            except Exception as e2:
                print(f"备选方案也失败: {e2}")
        
    def scoring_system(self):
        """多维度评分体系"""
        if not self.video_data:
            print("没有数据可供分析")
            return pd.DataFrame()
            
        print("\n=== 多维度评分 ===")
        
        df = pd.DataFrame(self.video_data)
        
        # 确保所有需要的列都存在并转换为数值类型
        required_columns = ['view', 'danmaku', 'comment', 'like', 'coin', 'favorite', 'share']
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0
            else:
                # 确保列是数值类型
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # 计算综合得分（简单相加）
        df['score'] = (df['view'] + df['danmaku']*10 + df['comment']*5 + 
                      df['like'] + df['coin']*2 + df['favorite']*2 + df['share']*3)
        
        # 按得分排序
        df_sorted = df.sort_values('score', ascending=False).reset_index(drop=True)
        
        print("综合评分排名:")
        for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
            # 从视频标题中提取BV号来匹配歌曲名称
            match = re.search(r'BV[A-Za-z0-9]+', row['bvid'])
            if match and match.group() in self.song_names:
                song_name = self.song_names[match.group()]
            else:
                # 如果无法匹配，则使用清理后的标题
                clean_title = row['title'].replace('【', '').replace('】', '').replace('《', '').replace('》', '')
                clean_title = re.sub(r'单依纯.*?-', '', clean_title)
                clean_title = re.sub(r'_.*', '', clean_title)
                clean_title = clean_title.strip()
                song_name = clean_title if clean_title else row['title'][:20]
                # 如果标题太长，只取前20个字符
                if len(song_name) > 20:
                    song_name = song_name[:20] + '...'
            
            print(f"{i:2d}. {song_name:<20} 得分: {row['score']:,.0f}")
        
        # 绘制高级排名图
        try:
            fig, ax = plt.subplots(figsize=(16, 10))
            top_videos = df_sorted.head(10)  # 前10名
            
            # 创建水平条形图
            y_pos = np.arange(len(top_videos))
            bars = ax.barh(y_pos, top_videos['score'], color=plt.cm.viridis(np.linspace(0, 1, len(top_videos))), alpha=0.8)
            
            # 添加数值标签
            for i, (bar, score) in enumerate(zip(bars, top_videos['score'])):
                width = bar.get_width()
                ax.annotate(f'{score:,.0f}',
                            xy=(width, bar.get_y() + bar.get_height()/2),
                            xytext=(5, 0),
                            textcoords="offset points",
                            ha='left', va='center', fontsize=10, fontweight='bold')
            
            ax.set_xlabel('综合得分', fontsize=14, fontproperties=label_font_prop)
            ax.set_title('视频综合得分排名（前10名）', fontsize=18, fontweight='bold', pad=20, fontproperties=big_title_font_prop)
            
            # 设置y轴标签为视频标题
            short_titles = []
            for _, row in top_videos.iterrows():
                # 从视频标题中提取BV号来匹配歌曲名称
                match = re.search(r'BV[A-Za-z0-9]+', row['bvid'])
                if match and match.group() in self.song_names:
                    song_name = self.song_names[match.group()]
                else:
                    # 如果无法匹配，则使用清理后的标题
                    clean_title = row['title'].replace('【', '').replace('】', '').replace('《', '').replace('》', '')
                    clean_title = re.sub(r'单依纯.*?-', '', clean_title)
                    clean_title = re.sub(r'_.*', '', clean_title)
                    clean_title = clean_title.strip()
                    song_name = clean_title if clean_title else row['title'][:20]
                    # 如果标题太长，只取前20个字符
                    if len(song_name) > 20:
                        song_name = song_name[:20] + '...'
                short_titles.append(song_name)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(short_titles, fontsize=11, fontproperties=chinese_font_prop)
            ax.invert_yaxis()  # 最高分在顶部
            
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig('视频综合得分排名_高级版.png', dpi=300, bbox_inches='tight', facecolor='white')
            plt.show()
        except Exception as e:
            print(f"绘制评分图时出错: {e}")
        
        return df_sorted

    def audience_engagement_analysis(self):
        """观众参与度分析"""
        if not self.video_data:
            print("没有数据可供分析")
            return
            
        df = pd.DataFrame(self.video_data)
        
        # 计算参与度指标
        # 参与度 = (弹幕数 + 评论数*2 + 点赞数*0.5 + 投币数*3 + 收藏数*3 + 分享数*4) / 播放量
        df['engagement_rate'] = (
            (df['danmaku'] + df['comment']*2 + df['like']*0.5 + 
             df['coin']*3 + df['favorite']*3 + df['share']*4) / df['view']
        ) * 100  # 转换为百分比
        
        # 按参与度排序
        df_sorted = df.sort_values('engagement_rate', ascending=False).reset_index(drop=True)
        
        # 绘制参与度排名图
        plt.figure(figsize=(14, 10))
        
        # 获取歌曲名称
        song_names = []
        for _, row in df_sorted.iterrows():
            match = re.search(r'BV[A-Za-z0-9]+', row['bvid'])
            if match and match.group() in self.song_names:
                song_name = self.song_names[match.group()]
            else:
                clean_title = row['title'].replace('【', '').replace('】', '').replace('《', '').replace('》', '')
                clean_title = re.sub(r'单依纯.*?-', '', clean_title)
                clean_title = re.sub(r'_.*', '', clean_title)
                clean_title = clean_title.strip()
                song_name = clean_title if clean_title else row['title'][:15]
                if len(song_name) > 15:
                    song_name = song_name[:15] + '...'
            song_names.append(song_name)
        
        # 绘制条形图
        bars = plt.bar(range(len(df_sorted)), df_sorted['engagement_rate'], 
                      color=plt.cm.viridis(np.linspace(0, 1, len(df_sorted))), alpha=0.8)
        
        # 添加数值标签
        for i, (bar, rate) in enumerate(zip(bars, df_sorted['engagement_rate'])):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{rate:.2f}%', ha='center', va='bottom', fontsize=10, fontproperties=chinese_font_prop)
        
        plt.xlabel('歌曲名称', fontsize=14, fontproperties=label_font_prop)
        plt.ylabel('观众参与度 (%)', fontsize=14, fontproperties=label_font_prop)
        plt.title('单依纯《歌手》节目各作品观众参与度排名', fontsize=18, fontweight='bold', pad=20, fontproperties=big_title_font_prop)
        plt.xticks(range(len(song_names)), song_names, rotation=45, ha='right', fontsize=12, fontproperties=chinese_font_prop)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig('观众参与度分析.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.show()
        
        # 输出统计信息
        print("\n=== 观众参与度分析 ===")
        print(f"平均参与度: {df['engagement_rate'].mean():.2f}%")
        print(f"最高参与度: {df['engagement_rate'].max():.2f}%")
        print(f"最低参与度: {df['engagement_rate'].min():.2f}%")
        
        # 输出排名
        print("\n参与度排名:")
        for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
            match = re.search(r'BV[A-Za-z0-9]+', row['bvid'])
            if match and match.group() in self.song_names:
                song_name = self.song_names[match.group()]
            else:
                clean_title = row['title'].replace('【', '').replace('】', '').replace('《', '').replace('》', '')
                clean_title = re.sub(r'单依纯.*?-', '', clean_title)
                clean_title = re.sub(r'_.*', '', clean_title)
                clean_title = clean_title.strip()
                song_name = clean_title if clean_title else row['title'][:20]
                if len(song_name) > 20:
                    song_name = song_name[:20] + '...'
            
            print(f"{i:2d}. {song_name:<20} 参与度: {row['engagement_rate']:.2f}%")
    
def main():
    """主函数"""
    print("开始分析单依纯《歌手》节目数据...")
    
    # 创建分析器实例
    analyzer = AdvancedSingerDataAnalyzer()
    
    # 加载数据
    analyzer.load_data()
    
    # 热度趋势分析
    analyzer.analyze_heat_trend()
    
    # 弹幕情感分析
    analyzer.analyze_danmaku_sentiment()
    
    # 关键词分析
    analyzer.extract_keywords()
    
    # 多维度评分
    analyzer.scoring_system()
    
    # 观众参与度分析（替代相关性分析）
    analyzer.audience_engagement_analysis()
    
    print("\n高级分析完成！已生成以下可视化图表:")
    print("1. 热度趋势分析_高级版.png")
    print("2. 弹幕情感分析_高级版.png")
    print("3. 弹幕词云_高级版.png")
    print("4. 视频综合得分排名_高级版.png")
    print("5. 观众参与度分析.png")

if __name__ == "__main__":
    main()