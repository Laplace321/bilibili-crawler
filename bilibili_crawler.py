#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bilibili视频弹幕爬虫脚本
功能：爬取特定Bilibili视频的弹幕数据和视频统计信息
"""

import requests
import json
import time
import re
import csv
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs


class BilibiliCrawler:
    def __init__(self, danmaku_limit=None):
        self.session = requests.Session()
        # 设置User-Agent，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        })
        self.danmaku_limit = danmaku_limit  # 弹幕抓取上限
        self.logged_in = False
        self.song_names = {}  # 存储从urls.txt中读取的歌曲名称

    def login(self, username, password):
        """
        用户登录功能（示例实现，实际需要根据B站登录机制调整）
        注意：B站有复杂的登录验证机制，包括验证码、加密等，这里仅为结构示例
        实际使用中建议通过浏览器获取cookies
        """
        print("注意：B站登录机制复杂，建议直接使用浏览器获取cookies")
        print("可以通过浏览器登录后，复制cookies到本程序")
        return False

    def set_cookies(self, cookies_str):
        """
        通过cookies字符串设置登录状态
        cookies_str: 浏览器中获取的cookies字符串
        """
        try:
            # 解析cookies字符串
            cookies = {}
            for item in cookies_str.split(';'):
                item = item.strip()
                if '=' in item:
                    key, value = item.split('=', 1)
                    cookies[key] = value
            
            # 设置cookies
            self.session.cookies.update(cookies)
            self.logged_in = True
            print("Cookies设置成功，已登录")
            return True
        except Exception as e:
            print(f"Cookies设置失败: {e}")
            return False

    def get_bvid_from_url(self, url):
        """
        从URL中提取BV号
        """
        parsed_url = urlparse(url)
        if parsed_url.netloc == 'www.bilibili.com':
            path_parts = parsed_url.path.split('/')
            for part in path_parts:
                if part.startswith('BV'):
                    return part
        return None

    def load_song_names(self, urls_file="urls.txt"):
        """
        从urls.txt文件中加载歌曲名称
        歌曲名称存储在每个URL的上一行注释中
        """
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                line = line.strip()
                # 检查是否是注释行（以#开头）
                if line.startswith('#') and i + 1 < len(lines):
                    # 获取注释内容作为歌曲名称（移除#号）
                    song_name = line[1:].strip()
                    # 获取下一行的URL
                    url_line = lines[i + 1].strip()
                    if url_line and not url_line.startswith('#'):
                        # 从URL中提取BV号
                        bvid = self.get_bvid_from_url(url_line)
                        if bvid:
                            self.song_names[bvid] = song_name
                            print(f"加载歌曲名称: {song_name} -> {bvid}")
            
            print(f"总共加载了 {len(self.song_names)} 个歌曲名称")
        except Exception as e:
            print(f"加载歌曲名称时发生异常: {e}")

    def get_video_info(self, url_or_bvid):
        """
        获取视频基本信息
        """
        # 判断输入是URL还是BV号
        if url_or_bvid.startswith('http'):
            bvid = self.get_bvid_from_url(url_or_bvid)
            if not bvid:
                print("无效的B站视频URL")
                return None
        else:
            bvid = url_or_bvid
        
        url = 'https://api.bilibili.com/x/web-interface/view'
        params = {'bvid': bvid}
        
        try:
            response = self.session.get(url, params=params)
            data = response.json()
            
            if data['code'] == 0:
                video_data = data['data']
                video_info = {
                    'bvid': bvid,
                    'aid': video_data['aid'],
                    'title': video_data['title'],
                    'desc': video_data['desc'],
                    'duration': video_data['duration'],
                    'pubdate': video_data['pubdate'],
                    'owner': video_data['owner']['name'],
                    'cid': video_data['cid'],  # 默认cid，用于弹幕爬取
                    'view': video_data['stat']['view'],      # 播放数
                    'danmaku': video_data['stat']['danmaku'], # 弹幕数
                    'comment': video_data['stat']['reply'],   # 评论数
                    'like': video_data['stat']['like'],       # 点赞数
                    'coin': video_data['stat']['coin'],       # 投币数
                    'favorite': video_data['stat']['favorite'], # 收藏数
                    'share': video_data['stat']['share'],     # 转发数
                }
                
                # 如果有对应的歌曲名称，则使用歌曲名称替换视频标题
                if bvid in self.song_names:
                    video_info['song_name'] = self.song_names[bvid]
                
                return video_info
            else:
                print(f"获取视频信息失败: {data['message']}")
                return None
        except Exception as e:
            print(f"获取视频信息时发生异常: {e}")
            return None

    def crawl_danmaku(self, oid):
        """
        爬取弹幕数据（当前弹幕）
        oid: 视频的cid
        """
        danmaku_url = f'https://comment.bilibili.com/{oid}.xml'
        danmakus = self._fetch_danmaku_from_url(danmaku_url)
        return danmakus

    def crawl_historical_danmaku(self, oid, date):
        """
        爬取历史弹幕数据
        oid: 视频的cid
        date: 日期，格式为 'YYYY-MM-DD'
        """
        if not self.logged_in:
            print("需要登录才能获取历史弹幕，请先设置cookies")
            return []
        
        danmaku_url = f'https://api.bilibili.com/x/v2/dm/history?type=1&oid={oid}&date={date}'
        danmakus = self._fetch_danmaku_from_api(danmaku_url)
        return danmakus

    def _fetch_danmaku_from_url(self, url):
        """
        从XML URL获取弹幕数据
        """
        try:
            response = self.session.get(url)
            response.encoding = 'utf-8'
            
            # 检查响应状态
            if response.status_code != 200:
                print(f"弹幕API响应异常，状态码: {response.status_code}")
                return []
            
            # 解析XML弹幕数据
            root = ET.fromstring(response.text)
            danmakus = []
            
            for elem in root.iter('d'):
                # 如果设置了弹幕抓取上限，达到上限则停止
                if self.danmaku_limit and len(danmakus) >= self.danmaku_limit:
                    break
                    
                # 弹幕属性在p标签中，用逗号分隔
                try:
                    attrs = elem.attrib['p'].split(',')
                    if len(attrs) >= 9 and elem.text:
                        danmaku_info = {
                            'content': elem.text,  # 弹幕内容
                            'time': float(attrs[0]),  # 弹幕出现时间（秒）
                            'type': int(attrs[3]),  # 弹幕类型
                            'fontsize': int(attrs[2]),  # 字体大小
                            'color': int(attrs[1]),  # 颜色
                            'timestamp': int(attrs[4]),  # 发送时间戳
                            'pool': int(attrs[5]),  # 弹幕池
                            'uid': attrs[6],  # 发送者UID
                            'row_id': attrs[7]  # 弹幕ID
                        }
                        danmakus.append(danmaku_info)
                except (ValueError, IndexError) as e:
                    # 忽略格式不正确的弹幕数据
                    continue
            
            return danmakus
        except Exception as e:
            print(f"爬取弹幕时发生异常: {e}")
            return []

    def _fetch_danmaku_from_api(self, url):
        """
        从API获取弹幕数据
        """
        try:
            response = self.session.get(url)
            data = response.json()
            
            # 检查响应状态
            if data['code'] != 0:
                print(f"弹幕API响应异常: {data['message']}")
                return []
            
            danmakus = []
            for elem in data.get('data', []):
                # 如果设置了弹幕抓取上限，达到上限则停止
                if self.danmaku_limit and len(danmakus) >= self.danmaku_limit:
                    break
                    
                try:
                    # 解析弹幕数据
                    danmaku_info = {
                        'content': elem.get('content', ''),  # 弹幕内容
                        'time': float(elem.get('progress', 0)) / 1000,  # 弹幕出现时间（毫秒转秒）
                        'type': elem.get('mode', 1),  # 弹幕类型
                        'fontsize': elem.get('fontsize', 25),  # 字体大小
                        'color': elem.get('color', 16777215),  # 颜色
                        'timestamp': elem.get('ctime', 0),  # 发送时间戳
                        'pool': elem.get('pool', 0),  # 弹幕池
                        'uid': elem.get('mid_hash', ''),  # 发送者UID
                        'row_id': elem.get('id_str', '')  # 弹幕ID
                    }
                    danmakus.append(danmaku_info)
                except (ValueError, IndexError) as e:
                    # 忽略格式不正确的弹幕数据
                    continue
            
            return danmakus
        except Exception as e:
            print(f"爬取弹幕时发生异常: {e}")
            return []

    def save_danmaku_to_csv(self, danmakus, filename):
        """
        将弹幕数据保存为CSV文件
        """
        if not danmakus:
            print("没有弹幕数据需要保存")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['content', 'time', 'type', 'fontsize', 'color', 'timestamp', 'pool', 'uid', 'row_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for danmaku in danmakus:
                    writer.writerow(danmaku)
            
            print(f"弹幕数据已保存至 {filename}")
        except Exception as e:
            print(f"保存弹幕数据时发生异常: {e}")

    def save_video_info_to_csv(self, video_info, filename):
        """
        将视频信息保存为CSV文件
        """
        if not video_info:
            print("没有视频信息需要保存")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['title', 'bvid', 'aid', 'owner', 'pubdate', 'duration', 
                              'view', 'danmaku', 'comment', 'like', 'coin', 'favorite', 'share', 'desc']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                # 创建一个只包含CSV定义字段的新字典
                video_info_to_save = {key: value for key, value in video_info.items() if key in fieldnames}
                
                # 如果有歌曲名称，则替换视频标题
                if 'song_name' in video_info:
                    video_info_to_save['title'] = video_info['song_name']
                
                # 转换时间戳为可读格式
                import datetime
                video_info_to_save['pubdate'] = datetime.datetime.fromtimestamp(
                    video_info_to_save['pubdate']).strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow(video_info_to_save)
            
            print(f"视频信息已保存至 {filename}")
        except Exception as e:
            print(f"保存视频信息时发生异常: {e}")

    def crawl_video_danmaku(self, url_or_bvid):
        """
        爬取指定视频的弹幕数据和视频信息
        """
        print("开始获取视频信息...")
        video_info = self.get_video_info(url_or_bvid)
        
        if not video_info:
            print("无法获取视频信息，程序退出")
            return False
        
        # 显示视频信息
        display_title = video_info.get('song_name', video_info['title'])
        print(f"视频标题: {display_title}")
        print(f"UP主: {video_info['owner']}")
        print(f"发布时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video_info['pubdate']))}")
        print(f"播放数: {video_info['view']}")
        print(f"弹幕数: {video_info['danmaku']}")
        print(f"评论数: {video_info['comment']}")
        print(f"点赞数: {video_info['like']}")
        print(f"投币数: {video_info['coin']}")
        print(f"收藏数: {video_info['favorite']}")
        print(f"转发数: {video_info['share']}")
        print(f"视频时长: {video_info['duration']}秒")
        print("开始爬取弹幕...")
        
        # 爬取弹幕
        danmakus = self.crawl_danmaku(video_info['cid'])
        print(f"共爬取 {len(danmakus)} 条弹幕")
        
        # 保存弹幕数据，使用视频标题作为文件名前缀
        # 如果有歌曲名称，则使用歌曲名称作为文件名前缀
        file_title = video_info.get('song_name', video_info['title'])
        
        # 清理标题中的非法字符
        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff\-\.]', '_', file_title).strip()
        safe_title = re.sub(r'\s+', '_', safe_title)  # 将空格替换为下划线
        # 确保文件名不以点或空格开头/结尾
        safe_title = safe_title.strip('. ')
        if not safe_title:
            safe_title = video_info['bvid']  # 如果处理后标题为空，则使用BV号
            
        danmaku_filename = f"{safe_title}_danmaku.csv"
        self.save_danmaku_to_csv(danmakus, danmaku_filename)
        
        # 保存视频信息
        video_info_filename = f"{safe_title}_info.csv"
        self.save_video_info_to_csv(video_info, video_info_filename)
        
        print("弹幕数据和视频信息爬取完成！")
        return True

    def crawl_batch_danmaku(self, urls_file):
        """
        批量爬取弹幕数据
        urls_file: 包含视频链接的文本文件路径
        """
        # 加载歌曲名称
        self.load_song_names(urls_file)
        
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                # 读取所有行，跳过空行和注释行（以#开头的行）
                urls = []
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释行
                    if line and not line.startswith('#'):
                        urls.append(line)
        except Exception as e:
            print(f"读取URL文件时发生异常: {e}")
            return
        
        print(f"从文件 {urls_file} 中读取到 {len(urls)} 个视频链接")
        
        success_count = 0
        for i, url in enumerate(urls, 1):
            print(f"\n正在处理第 {i}/{len(urls)} 个视频: {url}")
            try:
                if self.crawl_video_danmaku(url):
                    success_count += 1
                # 添加延时，避免请求过于频繁
                time.sleep(2)
            except Exception as e:
                print(f"处理视频 {url} 时发生异常: {e}")
        
        print(f"\n批量处理完成！成功处理 {success_count}/{len(urls)} 个视频")


def main():
    """
    主函数 - 使用示例
    """
    print("Bilibili弹幕爬虫")
    print("1. 单个视频弹幕抓取")
    print("2. 批量视频弹幕抓取")
    print("3. 登录并获取更多弹幕（需要cookies）")
    
    choice = input("请选择操作 (1-3): ").strip()
    
    if choice == "1":
        # 单个视频弹幕抓取
        crawler = BilibiliCrawler(danmaku_limit=None)
        # 加载歌曲名称
        crawler.load_song_names()
        video_input = input("请输入B站视频链接或BV号: ")
        
        if not video_input:
            print("输入不能为空")
            return
        
        crawler.crawl_video_danmaku(video_input)
        
    elif choice == "2":
        # 批量视频弹幕抓取
        crawler = BilibiliCrawler(danmaku_limit=None)
        urls_file = input("请输入包含视频链接的文本文件路径 (默认为 urls.txt): ").strip()
        if not urls_file:
            urls_file = "urls.txt"
        
        crawler.crawl_batch_danmaku(urls_file)
        
    elif choice == "3":
        # 登录并获取更多弹幕
        crawler = BilibiliCrawler(danmaku_limit=None)
        # 加载歌曲名称
        crawler.load_song_names()
        print("注意：需要获取B站登录后的cookies才能获取更多弹幕")
        print("请在浏览器中登录B站，然后按F12打开开发者工具")
        print("在Network标签中刷新页面，找到任意请求，复制Request Headers中的cookie值")
        cookies = input("请输入cookies: ").strip()
        
        if cookies and crawler.set_cookies(cookies):
            video_input = input("请输入B站视频链接或BV号: ")
            if not video_input:
                print("输入不能为空")
                return
            
            # 获取视频信息
            video_info = crawler.get_video_info(video_input)
            if video_info:
                display_title = video_info.get('song_name', video_info['title'])
                print(f"视频标题: {display_title}")
                print("可以选择获取当前弹幕或历史弹幕：")
                print("1. 当前弹幕")
                print("2. 历史弹幕")
                danmaku_choice = input("请选择 (1-2): ").strip()
                
                if danmaku_choice == "1":
                    crawler.crawl_video_danmaku(video_input)
                elif danmaku_choice == "2":
                    date = input("请输入日期 (格式 YYYY-MM-DD): ").strip()
                    if date:
                        danmakus = crawler.crawl_historical_danmaku(video_info['cid'], date)
                        print(f"共爬取 {len(danmakus)} 条历史弹幕")
                        
                        # 保存弹幕数据
                        file_title = video_info.get('song_name', video_info['title'])
                        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff\-\.]', '_', file_title).strip()
                        safe_title = re.sub(r'\s+', '_', safe_title)
                        safe_title = safe_title.strip('. ')
                        if not safe_title:
                            safe_title = video_info['bvid']
                            
                        danmaku_filename = f"{safe_title}_{date}_danmaku.csv"
                        crawler.save_danmaku_to_csv(danmakus, danmaku_filename)
                        
                        # 保存视频信息
                        video_info_filename = f"{safe_title}_{date}_info.csv"
                        crawler.save_video_info_to_csv(video_info, video_info_filename)
                    else:
                        print("日期不能为空")
                else:
                    print("无效选择")
        else:
            print("登录失败")
    else:
        print("无效的选择")


if __name__ == "__main__":
    main()