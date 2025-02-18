import requests
from bs4 import BeautifulSoup
import json
import csv

def get_page_info(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        articles = []
        selectors = ['article', '.post', '.article']
        article_elements = []
        
        for selector in selectors:
            article_elements = soup.select(selector)
            if article_elements:
                break
        
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
    if not data:
        print("没有数据可保存")
        return
        
    # 保存为JSON
    with open(f'{base_name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    # 保存为CSV
    with open(f'{base_name}.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"数据已保存到 {base_name}.json 和 {base_name}.csv")

def main():
    url = "https://kirkzheng.github.io/"
    print(f"正在获取 {url} 的文章信息...")
    articles = get_page_info(url)
    
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