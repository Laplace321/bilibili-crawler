#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终解决matplotlib中文显示问题的脚本
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np

def set_chinese_font():
    """
    设置中文字体，确保中文正确显示
    """
    # 查找系统中的中文字体文件
    zh_fonts = [f for f in fm.fontManager.ttflist if any(key in f.name for key in 
                ['SimHei', 'Songti', 'Hei', 'Microsoft', 'PingFang', 'ST', '华文', '黑体', '宋体'])]
    
    if zh_fonts:
        # 使用找到的第一个中文字体
        font_name = zh_fonts[0].name
        font_path = zh_fonts[0].fname
        print(f"使用中文字体: {font_name}")
        print(f"字体路径: {font_path}")
        
        # 设置字体
        plt.rcParams['font.sans-serif'] = [font_name]
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建字体属性对象
        chinese_font = fm.FontProperties(fname=font_path, size=12)
        title_font = fm.FontProperties(fname=font_path, size=14, weight='bold')
        
        return chinese_font, title_font
    else:
        print("未找到中文字体，使用默认设置")
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        return None, None

def create_test_charts():
    """
    创建测试图表验证中文显示
    """
    # 设置中文字体
    chinese_font, title_font = set_chinese_font()
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('中文图表测试', fontsize=16, fontweight='bold')
    
    # 图表1: 折线图
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    axes[0, 0].plot(x, y)
    axes[0, 0].set_title('正弦函数图', fontproperties=title_font)
    axes[0, 0].set_xlabel('X轴', fontproperties=chinese_font)
    axes[0, 0].set_ylabel('Y轴', fontproperties=chinese_font)
    
    # 图表2: 柱状图
    categories = ['类别A', '类别B', '类别C', '类别D']
    values = [23, 45, 56, 78]
    bars = axes[0, 1].bar(categories, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    axes[0, 1].set_title('柱状图示例', fontproperties=title_font)
    axes[0, 1].set_xlabel('分类', fontproperties=chinese_font)
    axes[0, 1].set_ylabel('数值', fontproperties=chinese_font)
    
    # 为柱状图添加数值标签
    for bar in bars:
        height = bar.get_height()
        axes[0, 1].annotate(f'{height}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontproperties=chinese_font)
    
    # 图表3: 散点图
    x = np.random.randn(100)
    y = np.random.randn(100)
    axes[1, 0].scatter(x, y, alpha=0.6)
    axes[1, 0].set_title('散点图示例', fontproperties=title_font)
    axes[1, 0].set_xlabel('X轴数据', fontproperties=chinese_font)
    axes[1, 0].set_ylabel('Y轴数据', fontproperties=chinese_font)
    
    # 图表4: 饼图
    sizes = [15, 30, 45, 10]
    labels = ['部分1', '部分2', '部分3', '部分4']
    axes[1, 1].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    axes[1, 1].set_title('饼图示例', fontproperties=title_font)
    
    plt.tight_layout()
    plt.savefig('最终中文测试图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print("中文测试图表已生成: 最终中文测试图.png")

def fix_existing_charts():
    """
    修复已有的图表中文显示问题
    """
    print("修复现有图表的中文显示...")
    
    # 重新运行高级分析脚本的主要功能
    print("请重新运行 advanced_analyze_data.py 脚本来生成正确显示中文的图表")

if __name__ == "__main__":
    print("开始解决matplotlib中文显示问题...")
    
    # 创建测试图表
    create_test_charts()
    
    # 提示修复现有图表
    fix_existing_charts()
    
    print("\n完成!")
    print("1. 已生成测试图表 '最终中文测试图.png' 验证中文显示")
    print("2. 请重新运行 'advanced_analyze_data.py' 生成最终分析图表")