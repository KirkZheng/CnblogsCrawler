import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QLineEdit, QMessageBox, QTabWidget, QHeaderView,
                             QStatusBar, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from main import get_page_info, save_data

# 定义样式表
STYLE_SHEET = """
QMainWindow {
    background-color: #f5f5f5;
}

QTabWidget::pane {
    border: 1px solid #cccccc;
    background-color: white;
}

QTabBar::tab {
    background-color: #e1e1e1;
    padding: 8px 20px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    border-top: 2px solid #4a90e2;
}

QLineEdit {
    padding: 6px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: white;
}

QPushButton {
    padding: 8px 16px;
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #357abd;
}

QPushButton:disabled {
    background-color: #cccccc;
}

QTableWidget {
    border: 1px solid #cccccc;
    gridline-color: #e1e1e1;
    background-color: white;
}

QTableWidget::item {
    padding: 5px;
}

QHeaderView::section {
    background-color: #f0f0f0;
    padding: 5px;
    border: none;
    border-right: 1px solid #cccccc;
    border-bottom: 1px solid #cccccc;
}
"""

class CrawlerThread(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            articles = get_page_info(self.url)
            self.finished.emit(articles)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('网站爬虫管理器')
        self.setGeometry(100, 100, 1000, 800)  # 增加窗口大小
        self.setStyleSheet(STYLE_SHEET)
        self.setup_ui()
        self.load_config()
        
        # 添加状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('就绪')
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar.addPermanentWidget(self.progress_bar)

    def setup_ui(self):
        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)  # 添加边距
        layout.setSpacing(15)  # 增加组件间距
        
        # 创建标签页
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # 爬虫控制页面
        crawler_tab = QWidget()
        crawler_layout = QVBoxLayout(crawler_tab)
        
        # URL输入区域
        url_layout = QHBoxLayout()
        url_label = QLabel('网站URL:')
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        crawler_layout.addLayout(url_layout)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        self.start_button = QPushButton('开始爬取')
        self.start_button.clicked.connect(self.start_crawler)
        button_layout.addWidget(self.start_button)
        crawler_layout.addLayout(button_layout)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('在结果中搜索...')
        self.search_input.returnPressed.connect(self.search_results)  # 添加回车键触发搜索
        search_button = QPushButton('搜索')
        search_button.clicked.connect(self.search_results)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        crawler_layout.addLayout(search_layout)
        
        # 搜索历史记录
        self.search_history = []
        self.original_articles = []
        
        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['标题', '作者'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # 设置表格的文本换行和列宽
        self.table.setWordWrap(True)
        self.table.verticalHeader().setDefaultSectionSize(40)  # 减小行高
        
        # 添加双击事件处理
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        crawler_layout.addWidget(self.table)

        tabs.addTab(crawler_tab, '爬虫控制')
        
        # 配置页面
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        
        # 超时设置
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel('超时设置(秒):')
        self.timeout_input = QLineEdit()
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_input)
        config_layout.addLayout(timeout_layout)
        
        # 重试次数设置
        retry_layout = QHBoxLayout()
        retry_label = QLabel('重试次数:')
        self.retry_input = QLineEdit()
        retry_layout.addWidget(retry_label)
        retry_layout.addWidget(self.retry_input)
        config_layout.addLayout(retry_layout)
        
        # 保存配置按钮
        save_config_button = QPushButton('保存配置')
        save_config_button.clicked.connect(self.save_config)
        config_layout.addWidget(save_config_button)
        
        tabs.addTab(config_tab, '配置')
    
    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                settings = config['settings']
                self.timeout_input.setText(str(settings['timeout']))
                self.retry_input.setText(str(settings['retry_times']))
                # 设置默认URL
                if config['sites']:
                    self.url_input.setText(config['sites'][0]['url'])
        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载配置文件失败: {str(e)}')
    
    def save_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config['settings']['timeout'] = int(self.timeout_input.text())
            config['settings']['retry_times'] = int(self.retry_input.text())
            
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, '成功', '配置已保存')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'保存配置失败: {str(e)}')
    
    def start_crawler(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, '错误', '请输入URL')
            return
        
        self.start_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 显示忙碌状态
        self.statusBar.showMessage('正在爬取数据...')
        
        self.crawler_thread = CrawlerThread(url)
        self.crawler_thread.finished.connect(self.on_crawler_finished)
        self.crawler_thread.error.connect(self.on_crawler_error)
        self.crawler_thread.start()

    def search_results(self):
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            # 如果搜索框为空，显示所有结果
            self.display_articles(self.original_articles)
            return
        
        # 将搜索词添加到历史记录
        if search_text not in self.search_history:
            self.search_history.append(search_text)
        
        # 在当前显示的结果中搜索
        filtered_articles = []
        for row in range(self.table.rowCount()):
            title = self.table.item(row, 0).text() if self.table.item(row, 0) else ''
            author = self.table.item(row, 1).text() if self.table.item(row, 1) else ''
            
            # 在标题和作者字段中搜索关键词
            if search_text in title.lower() or search_text in author.lower():
                article = {
                    'title': title,
                    'author': author,
                    'link': self.table.item(row, 0).data(Qt.UserRole) if self.table.item(row, 0) else ''
                }
                filtered_articles.append(article)
        
        # 显示过滤后的结果
        self.display_articles(filtered_articles)
        self.statusBar.showMessage(f'找到 {len(filtered_articles)} 条匹配结果')
    
    def display_articles(self, articles):
        """显示文章列表到表格中"""
        self.table.setRowCount(len(articles))
        for row, article in enumerate(articles):
            title_item = QTableWidgetItem(article.get('title', ''))
            title_item.setData(Qt.UserRole, article.get('link', ''))  # 将链接存储在标题项的用户数据中
            author_item = QTableWidgetItem(article.get('author', ''))
            author_link = article.get('author_link', '')
            if author_link:  # 只有当作者链接存在时才设置
                author_item.setData(Qt.UserRole, author_link)
            self.table.setItem(row, 0, title_item)
            self.table.setItem(row, 1, author_item)

    def on_crawler_finished(self, articles):
        self.progress_bar.setVisible(False)
        self.statusBar.showMessage('爬取完成')
        
        # 保存原始数据用于搜索
        self.original_articles = articles
        
        # 显示文章列表
        self.display_articles(articles)
        
        self.start_button.setEnabled(True)
        save_data(articles)
        QMessageBox.information(self, '成功', f'已爬取 {len(articles)} 篇文章')
    
    def on_crawler_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.statusBar.showMessage('爬取失败')
        self.start_button.setEnabled(True)
        QMessageBox.warning(self, '错误', f'爬取失败: {error_msg}')

    def on_cell_double_clicked(self, row, column):
        """处理表格单元格双击事件"""
        item = self.table.item(row, column)
        if item:
            if column == 0:  # 标题列
                link = item.data(Qt.UserRole)  # 从标题项的用户数据中获取链接
                if link:
                    import webbrowser
                    webbrowser.open(link)
            elif column == 1:  # 作者列
                author_link = item.data(Qt.UserRole)  # 从作者项的用户数据中获取链接
                if author_link:
                    import webbrowser
                    webbrowser.open(author_link)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()