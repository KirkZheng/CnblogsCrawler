# 导入所需的库
import requests  # 用于发送HTTP请求
from bs4 import BeautifulSoup  # 用于解析HTML内容
import json  # 用于处理JSON数据
import csv  # 用于处理CSV文件

def get_page_info(url):
    """
    获取指定URL页面的文章信息
    Args:
        url: 目标网页的URL
    Returns:
        articles: 包含文章信息的列表，每篇文章为一个字典
    """
    try:
        # 发送HTTP GET请求并获取响应
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        # 定义可能的文章选择器
        selectors = ['article', '.post', '.article']
        article_elements = []
        
        # 尝试不同的选择器来查找文章元素
        for selector in selectors:
            article_elements = soup.select(selector)
            if article_elements:
                break
        
        # 提取每篇文章的信息
        for article in article_elements:
            articles.append({
                'title': next((e.text.strip() for e in article.select('h1, h2, .title') if e), '未找到标题'),
                'publish_date': next((e.text.strip() for e in article.select('time, .date, .timestamp') if e), '未找到发布时间'),
                'link': next((a.get('href', '') for a in article.select('a') if 'href' in a.attrs), '')
            })
        
        return articles
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return []

def save_data(data, base_name='articles'):
    """
    将数据保存为JSON和CSV格式
    Args:
        data: 要保存的数据列表
        base_name: 保存文件的基础名称
    """
    if not data:
        print("没有数据可保存")
        return
        
    # 保存为JSON格式
    with open(f'{base_name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    # 保存为CSV格式
    with open(f'{base_name}.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"数据已保存到 {base_name}.json 和 {base_name}.csv")

def main():
    """
    主函数：爬取指定网页的文章信息并保存
    """
    url = "https://kirkzheng.github.io/"
    print(f"正在获取 {url} 的文章信息...")
    # 获取文章信息
    articles = get_page_info(url)
    
    # 显示和保存结果
    if articles:
        print(f"\n找到 {len(articles)} 篇文章")
        for article in articles:
            print(f"\n标题: {article['title']}")
            print(f"发布时间: {article['publish_date']}")
            print(f"链接: {article['link']}")
        save_data(articles)
    else:
        print("未找到任何文章信息")

if __name__ == '__main__':
    main()