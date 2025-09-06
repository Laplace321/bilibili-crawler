#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复matplotlib中文字体显示问题的最终脚本
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import os

def setup_chinese_fonts():
    """
    设置正确的中文字体
    """
    print("正在查找系统中的中文字体...")
    
    # 查找系统中的中文字体
    all_fonts = fm.fontManager.ttflist
    chinese_fonts = []
    
    # 查找真正的中文字体
    for font in all_fonts:
        # 检查字体文件名是否包含中文字体标识
        if any(key in font.fname.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'pmingliu', 'hei', 'song', 'kai']):
            chinese_fonts.append(font)
        # 检查字体名称是否包含中文字体标识
        elif any(key in font.name.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'pmingliu', 'hei', 'song', 'kai']):
            chinese_fonts.append(font)
    
    print(f"找到 {len(chinese_fonts)} 个可能的中文字体")
    
    # 如果找不到明确的中文字体，尝试查找系统字体
    if not chinese_fonts:
        print("未找到明确的中文字体，尝试查找系统字体...")
        # 在常见位置查找中文字体文件
        font_paths = [
            '/System/Library/Fonts/',  # macOS
            '/Library/Fonts/',          # macOS
            'C:/Windows/Fonts/',        # Windows
            '/usr/share/fonts/'         # Linux
        ]
        
        chinese_font_files = []
        for path in font_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if any(key in file.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'hei', 'song', 'kai']):
                            chinese_font_files.append(os.path.join(root, file))
        
        print(f"找到 {len(chinese_font_files)} 个中文字体文件")
        
        # 注册找到的字体文件
        for font_file in chinese_font_files[:5]:  # 只注册前5个
            try:
                font_name = os.path.splitext(os.path.basename(font_file))[0]
                fm.fontManager.addfont(font_file)
                print(f"注册字体: {font_name} ({font_file})")
            except Exception as e:
                print(f"注册字体失败 {font_file}: {e}")
    
    # 再次查找中文字体
    all_fonts = fm.fontManager.ttflist
    chinese_fonts = [f for f in all_fonts if 
                    any(key in f.name.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'pmingliu', 'hei', 'song', 'kai']) or
                    any(key in f.fname.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'pmingliu', 'hei', 'song', 'kai'])]
    
    if chinese_fonts:
        # 使用找到的中文字体
        font_names = [f.name for f in chinese_fonts[:5]]
        plt.rcParams['font.sans-serif'] = font_names + ['sans-serif']
        print(f"使用中文字体: {font_names}")
    else:
        # 备选方案：使用系统默认字体并尝试支持中文
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
        print("使用备选字体方案")
    
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False
    
    # 设置Seaborn样式
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    
    return chinese_fonts

def create_test_plot():
    """
    创建测试图表验证中文显示
    """
    print("创建测试图表...")
    
    # 创建简单图表
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 绘制简单数据
    x = [1, 2, 3, 4, 5]
    y = [2, 5, 3, 8, 7]
    ax.plot(x, y, marker='o')
    
    # 添加中文标签
    ax.set_title('中文标题测试', fontsize=16, pad=20)
    ax.set_xlabel('X轴标签（中文）', fontsize=12)
    ax.set_ylabel('Y轴标签（中文）', fontsize=12)
    
    # 添加中文图例
    ax.legend(['数据系列'], loc='upper left')
    
    # 添加网格
    ax.grid(True, alpha=0.3)
    
    # 保存图表
    plt.tight_layout()
    plt.savefig('中文显示测试_final.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    
    print("测试图表已保存为 '中文显示测试_final.png'")

def fix_advanced_analyze_script():
    """
    修复高级数据分析脚本中的中文字体设置
    """
    print("修复高级数据分析脚本...")
    
    script_path = '/Users/laplacetong/bilibili-crawler/advanced_analyze_data.py'
    
    if not os.path.exists(script_path):
        print(f"脚本文件不存在: {script_path}")
        return False
    
    # 读取脚本内容
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换字体设置部分
    font_setup_code = '''# 尝试设置中文字体
def set_chinese_font():
    """
    设置中文字体以确保正确显示中文
    """
    # 查找可用的中文字体
    all_fonts = fm.fontManager.ttflist
    chinese_fonts = [f for f in all_fonts if 
                    any(key in f.name.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'pmingliu', 'hei', 'song', 'kai']) or
                    any(key in f.fname.lower() for key in ['simhei', 'simsun', 'msyh', 'mingliu', 'pmingliu', 'hei', 'song', 'kai'])]
    
    if chinese_fonts:
        # 使用找到的中文字体
        font_names = [f.name for f in chinese_fonts[:5]]
        plt.rcParams['font.sans-serif'] = font_names + ['sans-serif']
        print(f"使用中文字体: {font_names[0] if font_names else '未知'}")
    else:
        # 备选方案：使用系统默认字体并尝试支持中文
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
        print("使用备选字体方案")
    
    # 解决负号显示问题
    plt.rcParams['axes.unicode_minus'] = False
    
    # 设置Seaborn样式
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    
    return chinese_fonts

# 设置中文字体
set_chinese_font()'''
    
    # 查找并替换原有的字体设置代码
    if '# 尝试设置中文字体' in content:
        # 如果已有字体设置函数，替换整个函数
        import re
        pattern = r'# 尝试设置中文字体.*?(?=class|\nif __name__ == "__main__":)'
        content = re.sub(pattern, font_setup_code, content, flags=re.DOTALL)
    else:
        # 如果没有字体设置函数，在导入语句后添加
        insert_pos = content.find('\n\n# 设置中文字体和解决负号显示问题')
        if insert_pos == -1:
            insert_pos = content.find('\nclass ')
        if insert_pos == -1:
            insert_pos = len(content)
        
        content = content[:insert_pos] + '\n\n' + font_setup_code + '\n' + content[insert_pos:]
    
    # 写回文件
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("高级数据分析脚本修复完成")
    return True

def main():
    """
    主函数
    """
    print("开始修复中文字体显示问题...")
    
    # 设置中文字体
    chinese_fonts = setup_chinese_fonts()
    
    # 创建测试图表
    create_test_plot()
    
    # 修复高级数据分析脚本
    fix_advanced_analyze_script()
    
    print("\n修复完成!")
    print("1. 已设置正确的中文字体")
    print("2. 已生成测试图表 '中文显示测试_final.png'")
    print("3. 已修复高级数据分析脚本")
    print("4. 现在可以重新运行 'advanced_analyze_data.py' 生成正确显示中文的图表")

if __name__ == "__main__":
    main()