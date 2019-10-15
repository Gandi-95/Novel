import time
import random
import newspaper
import threading
import os



s = threading.BoundedSemaphore(value=10)

class downThread(threading.Thread):

    def __init__(self,novelName, tempList,index):
        threading.Thread.__init__(self)
        self.novelName = novelName
        self.tempList = tempList
        self.index = index

    def run(self):
        s.acquire()
        novel_path = self.createdirs()+'/{}temp'+str(self.index)+'.txt'
        count = 0
        txt = '    '+self.novelName+'\n\n'
        for catalog in self.tempList:
            count += 1
            title = '    ' + list(catalog.keys())[0]
            url = list(catalog.values())[0]
            text = self.getText(url)
            print('正在下载：' + title)
            txt += '%s\n\n%s\n%s' % (title, text, '\n\n')
            if count == 30:
                count = 0
                with open(novel_path.format(self.novelName), 'a',encoding='utf-8') as f:
                    f.write(txt)
                txt = ''
        if (count != 0):
            with open(novel_path.format(self.novelName), 'a',encoding='utf-8') as f:
                f.write(txt)
        print(novel_path.format(self.novelName) + " 下载完成。")
        s.release()

    def createdirs(self):
        print(os.getcwd())
        path = os.getcwd()+"/data/"

        # 判断结果
        if not os.path.exists(path):
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)
        return path

    def getText(self, url):
        try:
            # time.sleep(random.randint(1, 10) / 10)
            a = newspaper.Article(url, language='zh')
            a.download()
            a.parse()
            text = '    ' + a.text
        except Exception as e:
            time.sleep(random.randint(1, 10) / 10)
            print("下载失败:" + url)
            print(e)
            text = self.getText(url)
        return text.replace('\n\n', '\n\n    ')

    def writeTempText(self):
        print()


def createdirs():
    print(os.getcwd())
    path = os.getcwd()+"/data/"

    # 判断结果
    if not os.path.exists(path):
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
    return path

def getText( url):
    try:
        time.sleep(1)
        a = newspaper.Article(url, language='zh')
        a.download()
        a.parse()
        text = '    ' + a.text
    except Exception as e:
        time.sleep(random.randint(1, 10) / 10)
        print("下载失败:" + url)
        print(e)
        text = getText(url)
    return text.replace('\n\n', '\n\n    ')



def main(catalog_list,novelName):
    novel_path = createdirs() + '/{}.txt'
    count = 0
    txt = '    ' + novelName + '\n\n'
    for catalog in catalog_list:
        count += 1
        title = '    ' + list(catalog.keys())[0]
        url = list(catalog.values())[0]
        text = getText(url)
        print('正在下载：' + title)
        txt += '%s\n\n%s\n%s' % (title, text, '\n\n')
        if count == 30:
            count = 0
            with open(novel_path.format(novelName), 'a',encoding='utf-8') as f:
                f.write(txt)
            txt = ''
    if (count != 0):
        with open(novel_path.format(novelName), 'a',encoding='utf-8') as f:
            f.write(txt)
    print(novel_path.format(novelName) + " 下载完成。")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))






def thread(catalog_list,novelName):
    tempListLen = len(catalog_list) // 9;
    tempLists = [[]] * 10
    print(tempLists)

    for i in range(10):
        if i == 10:
            tempLists[i] = catalog_list[(i * tempListLen): len(catalog_list)]
        else:
            tempLists[i] = catalog_list[((i * tempListLen)): ((i + 1) * tempListLen)]

    for index, tempList in enumerate(tempLists):
        thread = downThread(novelName, tempList, index)
        thread.start()


# 大清隐龙  https://www.cnblogs.com/IT-Scavenger/p/9883489.html
def start(catalog_list,novelName):
   # thread(catalog_list,novelName)
   main(catalog_list, novelName)

