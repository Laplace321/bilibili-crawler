#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复图表中文字体显示问题的脚本
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import os

def setup_chinese_font():
    """
    设置中文字体，解决中文显示为方框的问题
    """
    # 查找系统中的中文字体
    zh_fonts = [f.name for f in fm.fontManager.ttflist if any(key in f.name for key in 
                ['Sim', 'Song', 'Hei', 'Kai', 'Microsoft', 'PingFang', 'ST', '华文', '黑体', '宋体', '楷体'])]
    
    print("找到的中文字体:")
    for font in zh_fonts[:10]:  # 只显示前10个
        print(f"  - {font}")
    
    if zh_fonts:
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = zh_fonts
        print(f"\n已设置中文字体: {zh_fonts[0]}")
    else:
        # 如果找不到中文字体，使用默认字体并尝试解决
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
        print("\n未找到中文字体，使用默认字体")
    
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False
    
    # 设置Seaborn样式
    sns.set_style("whitegrid")
    
    return zh_fonts

def test_chinese_display():
    """
    测试中文显示效果
    """
    # 设置中文字体
    zh_fonts = setup_chinese_font()
    
    # 创建测试图表
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 测试中文标题
    ax.set_title('中文标题测试', fontsize=16, pad=20)
    
    # 测试中文坐标轴标签
    ax.set_xlabel('X轴标签（中文）', fontsize=12)
    ax.set_ylabel('Y轴标签（中文）', fontsize=12)
    
    # 测试中文图例
    ax.plot([1, 2, 3], [1, 4, 2], label='数据系列（中文）')
    ax.legend()
    
    # 显示网格
    ax.grid(True, alpha=0.3)
    
    # 保存测试图表
    plt.tight_layout()
    plt.savefig('中文显示测试.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print("中文显示测试完成，图表已保存为 '中文显示测试.png'")
    return zh_fonts

def fix_existing_charts():
    """
    重新生成已有的图表，确保中文正确显示
    """
    print("重新生成现有图表以修复中文显示...")
    
    # 这里可以添加重新生成特定图表的代码
    # 由于我们已经修改了高级分析脚本，重新运行即可
    
    print("请重新运行 advanced_analyze_data.py 以生成修复后的图表")

if __name__ == "__main__":
    print("开始修复中文字体显示问题...")
    
    # 测试中文显示
    fonts = test_chinese_display()
    
    # 重新生成图表
    fix_existing_charts()
    
    print(f"\n可用中文字体数量: {len(fonts)}")
    if fonts:
        print("推荐的中文字体:")
        for font in fonts[:5]:
            print(f"  - {font}")
    else:
        print("建议安装中文字体以获得更好的显示效果")