import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import csv
from pathlib import Path

def get_page_info(url):
    try:
        # 设置请求超时时间为10秒
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 存储文章信息的列表
        articles = []
        
        # 查找所有文章元素（这里的选择器需要根据实际网页结构调整）
        article_elements = soup.select('article') or soup.select('.post') or soup.select('.article')
        
        for article in article_elements:
            article_info = {}
            
            # 尝试获取标题
            title_element = article.select_one('h1') or article.select_one('h2') or article.select_one('.title')
            article_info['title'] = title_element.text.strip() if title_element else '未找到标题'
            
            # 尝试获取发布时间
            date_element = article.select_one('time') or article.select_one('.date') or article.select_one('.timestamp')
            article_info['publish_date'] = date_element.text.strip() if date_element else '未找到发布时间'
            
            # 尝试获取文章链接
            link_element = article.select_one('a')
            article_info['link'] = link_element['href'] if link_element and 'href' in link_element.attrs else ''
            
            articles.append(article_info)
        
        return articles
        
    except requests.Timeout:
        print("请求超时")
        return []
    except requests.RequestException as e:
        print(f"请求错误: {str(e)}")
        return []
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return []

def save_to_json(data, filename='articles.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到 {filename}")

def save_to_csv(data, filename='articles.csv'):
    if not data:
        print("没有数据可保存")
        return
        
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"数据已保存到 {filename}")

def main():
    url = "https://kirkzheng.github.io/"
    print(f"正在获取 {url} 的文章信息...")
    articles = get_page_info(url)
    
    if articles:
        print(f"\n找到 {len(articles)} 篇文章")
        for article in articles:
            print("\n文章信息:")
            print(f"标题: {article['title']}")
            print(f"发布时间: {article['publish_date']}")
            print(f"链接: {article['link']}")
        
        # 保存数据
        save_to_json(articles)
        save_to_csv(articles)
    else:
        print("未找到任何文章信息")

if __name__ == '__main__':
    main()