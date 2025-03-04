# 导入所需的库
import requests  # 用于发送HTTP请求
from bs4 import BeautifulSoup  # 用于解析HTML内容
import json  # 用于处理JSON数据
import csv  # 用于处理CSV文件

def get_page_info(url, max_articles=100):
    """获取指定URL页面的文章信息，默认随机爬取100篇文章"""
    import random
    # 检查是否是博客园URL
    if 'cnblogs.com' in url:
        try:
            # 设置请求头，模拟浏览器访问
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Referer': 'https://www.cnblogs.com'
            }
            
            articles = []
            page = 1
            
            # 循环获取文章，直到达到目标数量
            while len(articles) < max_articles:
                # 构造分页URL
                if page > 1:
                    paged_url = f"{url}?page={page}" if '?' not in url else f"{url}&page={page}"
                else:
                    paged_url = url
                
                # 发送请求获取页面内容
                response = requests.get(paged_url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                    # 判断是否为博文页面
                if '/p/' in url:
                    # 提取文章信息
                    title = soup.select_one('#cb_post_title_url').text.strip() if soup.select_one('#cb_post_title_url') else ''
                    author = soup.select_one('#author_profile_detail a').text.strip() if soup.select_one('#author_profile_detail a') else ''
                    publish_date = soup.select_one('#post-date').text.strip() if soup.select_one('#post-date') else ''
                    content = soup.select_one('#cnblogs_post_body').get_text(strip=True) if soup.select_one('#cnblogs_post_body') else ''
                    read_count = soup.select_one('#post_view_count').text.strip() if soup.select_one('#post_view_count') else '0'
                    comment_count = soup.select_one('#post_comment_count').text.strip() if soup.select_one('#post_comment_count') else '0'
                    
                    articles.append({
                        'title': title,
                        'publish_date': publish_date,
                        'link': url,
                        'author': author,
                        'category': '博客园文章',
                        'summary': content[:200] + '...' if len(content) > 200 else content,
                        'content': content,
                        'read_count': read_count,
                        'comment_count': comment_count,
                        'retweet_count': '0',
                        'like_count': '0'
                    })
                else:
                    # 获取博客园主页的文章列表
                    article_list = soup.select('.post-item')
                    for article in article_list:
                        try:
                            title_elem = article.select_one('.post-item-title')
                            title = title_elem.text.strip() if title_elem else ''
                            link = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ''
                            author_elem = article.select_one('.post-item-author')
                            author = author_elem.text.strip() if author_elem else ''
                            author_link = author_elem['href'] if author_elem and 'href' in author_elem.attrs else ''
                            # 确保作者链接格式正确
                            if author_link and not author_link.startswith('http'):
                                author_link = 'https://www.cnblogs.com' + author_link
                            publish_date = article.select_one('.post-item-foot .post-item-date').text.strip() if article.select_one('.post-item-foot .post-item-date') else ''
                            summary = article.select_one('.post-item-summary').get_text(strip=True) if article.select_one('.post-item-summary') else ''
                            read_count = article.select_one('.post-item-view-count').text.strip().replace('阅读', '').strip() if article.select_one('.post-item-view-count') else '0'
                            comment_count = article.select_one('.post-item-comment-count').text.strip().replace('评论', '').strip() if article.select_one('.post-item-comment-count') else '0'
                            
                            # 对于主页文章，我们不需要获取完整内容
                            articles.append({
                                'title': title,
                                'publish_date': publish_date,
                                'link': link,
                                'author': author,
                                'author_link': author_link,
                                'category': '博客园文章',
                                'summary': summary,
                                'content': summary,  # 对于主页文章，使用摘要作为内容
                                'read_count': read_count.replace('阅读','').strip(),
                                'comment_count': comment_count.replace('评论','').strip(),
                                'retweet_count': '0',
                                'like_count': '0'
                            })
                        except Exception as e:
                            print(f'处理博客园文章时出错: {str(e)}')
                            continue
            
                # 如果没有找到更多文章，退出循环
                if not article_list:
                    break
                
                page += 1
                
                # 如果已经获取足够的文章，退出循环
                if len(articles) >= max_articles:
                    break
            
            if not articles:
                raise Exception('未找到任何文章')
            
            # 如果文章数量超过要求，随机选择指定数量的文章
            if len(articles) > max_articles:
                articles = random.sample(articles, max_articles)
            return articles
            
        except Exception as e:
            raise Exception(f'博客园爬取错误: {str(e)}')
    # 如果不是特定网站，使用通用爬取逻辑
    else:
        raise Exception('不支持的网站，目前只支持博客园')
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

# 移除命令行入口，保留核心功能供GUI调用