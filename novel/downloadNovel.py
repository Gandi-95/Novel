import time
import random
import newspaper
import threading


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


s = threading.BoundedSemaphore(value=10)


class downThread(threading.Thread):

    def __init__(self, tempList):
        threading.Thread.__init__(self)
        self.tempList = tempList

    def run(self):
        s.acquire()
        for list in self.tempList:
            print(list)
        s.release()

# 大清隐龙
def start(catalog_list):
    tempListLen = len(catalog_list) // 10;
    tempLists = [[]] * 10
    print(tempLists)

    for i in range(10):
        if i == 10:
            tempLists[i] = catalog_list[(i  * tempListLen): len(catalog_list)]
        else:
            tempLists[i] = catalog_list[((i * tempListLen)): ((i+1) * tempListLen)]

    for tempList in tempLists:
        thread = downThread(tempList)
        thread.start()
    print()
