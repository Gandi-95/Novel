import novelSource
import time

if __name__ == '__main__':
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    novelName = input('请输入书名:')
    novelsource = novelSource.biquge5200()
    novelsource.init(novelName)