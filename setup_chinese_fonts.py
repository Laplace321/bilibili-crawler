#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置matplotlib中文字体的脚本
确保图表中的中文能正确显示
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import os

def setup_matplotlib_chinese():
    """
    配置matplotlib以正确显示中文
    """
    print("正在配置matplotlib中文字体...")
    
    # 查找系统中的中文字体
    zh_fonts = [f for f in fm.fontManager.ttflist if any(key in f.name for key in 
                ['SimHei', 'Songti', 'Hei', 'Kai', 'Microsoft', 'PingFang', 'ST', '华文', '黑体', '宋体', '楷体'])]
    
    # 优先使用更常见的中文字体
    preferred_fonts = ['SimHei', 'Microsoft YaHei', 'Heiti TC', 'Songti SC', 'STHeiti', 'STSong']
    available_fonts = [f.name for f in zh_fonts if any(pf in f.name for pf in preferred_fonts)]
    
    print(f"找到 {len(zh_fonts)} 个中文字体")
    print(f"推荐字体: {len(available_fonts)} 个")
    
    if available_fonts:
        print("使用推荐中文字体:")
        plt.rcParams['font.sans-serif'] = available_fonts
        for font in available_fonts[:5]:  # 显示前5个
            print(f"  - {font}")
    elif zh_fonts:
        print("使用系统中文字体:")
        font_names = [f.name for f in zh_fonts[:5]]
        plt.rcParams['font.sans-serif'] = font_names
        for font in font_names:
            print(f"  - {font}")
    else:
        print("未找到中文字体，使用备选方案")
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
    
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False
    
    # 设置Seaborn样式
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    
    print("matplotlib中文字体配置完成")
    return available_fonts if available_fonts else ([f.name for f in zh_fonts] if zh_fonts else [])

def test_chinese_display():
    """
    测试中文显示效果
    """
    print("\n测试中文显示效果...")
    
    # 创建测试图表
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 第一个子图 - 折线图
    ax1.plot([1, 2, 3, 4], [1, 4, 2, 3], 'o-', linewidth=2, markersize=8)
    ax1.set_title('测试标题 - 折线图', fontsize=14, pad=10)
    ax1.set_xlabel('X轴标签', fontsize=12)
    ax1.set_ylabel('Y轴标签', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # 第二个子图 - 柱状图
    bars = ax2.bar(['类别A', '类别B', '类别C'], [3, 7, 5], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax2.set_title('测试标题 - 柱状图', fontsize=14, pad=10)
    ax2.set_xlabel('分类', fontsize=12)
    ax2.set_ylabel('数值', fontsize=12)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('中文显示测试图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print("中文显示测试完成，图表已保存为 '中文显示测试图.png'")

def apply_to_all_scripts():
    """
    为所有数据分析脚本应用中文字体配置
    """
    print("\n为所有脚本应用中文字体配置...")
    
    # 获取中文字体列表
    zh_fonts = setup_matplotlib_chinese()
    
    font_config_code = f"""
# 设置中文字体和解决负号显示问题
import matplotlib.font_manager as fm
# 查找系统中的中文字体
zh_fonts = [f.name for f in fm.fontManager.ttflist if any(key in f.name for key in 
            ['SimHei', 'Songti', 'Hei', 'Kai', 'Microsoft', 'PingFang', 'ST', '华文', '黑体', '宋体', '楷体'])]

# 优先使用更常见的中文字体
preferred_fonts = ['SimHei', 'Microsoft YaHei', 'Heiti TC', 'Songti SC', 'STHeiti', 'STSong']
available_fonts = [f for f in zh_fonts if any(pf in f for pf in preferred_fonts)]

if available_fonts:
    plt.rcParams['font.sans-serif'] = available_fonts
else:
    # 如果找不到推荐字体，使用系统中任何可用的中文字体
    if zh_fonts:
        plt.rcParams['font.sans-serif'] = zh_fonts[:5]  # 使用前5个中文字体
    else:
        # 最后的备选方案
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']

plt.rcParams['axes.unicode_minus'] = False
"""
    
    print("中文字体配置代码已生成")
    return font_config_code

if __name__ == "__main__":
    # 配置中文字体
    fonts = setup_matplotlib_chinese()
    
    # 测试中文显示
    test_chinese_display()
    
    # 应用到所有脚本的说明
    apply_to_all_scripts()
    
    print(f"\n总结:")
    print(f"- 已配置matplotlib中文字体支持")
    print(f"- 可用中文字体数量: {len(fonts)}")
    if fonts:
        print(f"- 推荐字体: {fonts[0] if len(fonts) > 0 else 'N/A'}")
    print(f"- 已生成测试图表 '中文显示测试图.png'")
    print(f"- 现在可以正确生成包含中文的图表了")