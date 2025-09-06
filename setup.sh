#!/bin/bash

echo "正在创建Python虚拟环境..."
python3 -m venv venv

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装依赖包..."
pip install -r requirements.txt

echo "环境设置完成！"
echo ""
echo "要激活虚拟环境，请运行以下命令："
echo "source venv/bin/activate"
echo ""
echo "要运行爬虫，请执行："
echo "python bilibili_crawler.py"