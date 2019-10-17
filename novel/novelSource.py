import requests
from bs4 import BeautifulSoup
import downloadNovel

import urllib.parse
import sys


class source:
    # 定义网站base_url和搜索url
    def __init__(self):
        self.host_url = ""
        self.seach_url = ''



    # 获取网站的内容
    def get_Html(self,url,encoding='utf-8'):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept - Encoding': 'gzip, deflate, br',
            'Accept - Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        html_doc = requests.get(url, headers=headers)
        html_doc.encoding = encoding
        soup = BeautifulSoup(html_doc.text, 'html.parser')
        return soup

    def seachUrl(self, novelName):
        return self.seach_url.format(novelName)

    # 获取搜索到的小说
    def getNovels(self, novels_soup):
        print()

    # 显示搜索到的小说
    def showSearchNovel(self, novels):
        if novels != None:
            index = 1
            print('搜索结果:')
            for item in novels:
                a = '%d：%s' % (index, list(item.keys())[0])
                index += 1
                print(a)

    # 选择搜索到的小说
    def selectNovel(self, str, len):
        index = input(str)
        try:
            index = int(index)
            if (index <= 0 and index > len):
                index = self.selectNovel('请输入正确下载的序号:', len)
        except Exception as e:
            index = self.selectNovel('请输入正确下载的序号:', len)
        return index

    # 获取选择小说的目录，返回{title:herf}的列表
    def getCatalog(self, novel):
        print()

    def init(self, novelName):
        url = self.seachUrl(novelName)
        print(url)
        novels_soup = self.get_Html(url)
        novels = self.getNovels(novels_soup)
        self.showSearchNovel(novels)
        index = self.selectNovel('请输入需要下载的序号:', len(novels))
        catalog_list = self.getCatalog(novels[index - 1])
        downloadNovel.start(catalog_list, novelName)


# ——————————————————————————笔趣阁系列————————————————————————————
class biquge(source):
    def findAllNovels(self):
        return 'td', 'odd'

    def getNovelsInfo(self,a):
        title = a.get_text()
        href = a.get('href')
        print(title + href)
        return {title: href}

    def getNovels(self, novels_soup):
        seach_result_list = []
        td = novels_soup.find_all(self.findAllNovels())
        for item in td:
            a = item.a
            if a != None:
                seach_result_list.append(self.getNovelsInfo(a))
        return seach_result_list


    def getCatalogHtml(self,url):
        return self.get_Html(list(url))

    def getCatalogInfo(self, a):
        title = a.get_text()
        href = a.get('href')
        print(title + href)
        return {title:href}

    def getCatalog(self, novel):
        catalog_soup = self.getCatalogHtml(list(novel.values())[0])
        catalog = catalog_soup.find_all('dd')
        catalog_list = []
        for item in catalog:
            a = item.a
            if a != None:
                catalog_list.append(self.getCatalogInfo(a))

        # 前面9章为最新更新的章节，所以过滤
        if catalog_list != None:
            lenght = len(catalog_list)
            if lenght < 18:
                catalog_list = catalog_list[lenght // 2:lenght]
            else:
                catalog_list = catalog_list[9:lenght]

        return catalog_list


# ——————————————https://www.biquge5200.cc/————————————————————————————————
class biquge5200(biquge):
    def __init__(self):
        self.host_url = "https://www.biquge5200.cc"
        self.seach_url = 'https://www.biquge5200.cc/modules/article/search.php?searchkey={}'

    def findAllNovels(self):
        return 'td', 'odd'


# ————————————————https://www.biqugex.com/————————————————————————————————
class biqugex(biquge):
    def __init__(self):
        self.host_url ='https://www.biqugex.com'
        self.seach_url = 'https://so.biqusoso.com/s.php?ie=gbk&siteid=biqugex.com&s=9157106854577873494&q={}'

    def seachUrl(self, novelName):
        return self.seach_url.format(urllib.parse.quote(novelName.encode('gbk')))

    def findAllNovels(self):
        return 'li'

    def getNovelsInfo(self,a):
        title = a.get_text()
        href = a.get('href').replace('/goto/id/','_')+"/"
        return {title:href}

    def getCatalogHtml(self,url):
        return self.get_Html(url,'gb18030')

    def getCatalogInfo(self, a):
        title = a.get_text()
        href = self.host_url+a.get('href')

        return {title:href}
