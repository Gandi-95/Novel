import novelSource




if __name__ == '__main__':
    novelName = input('请输入书名:')
    novelsource = novelSource.biquge5200()
    novelsource.init(novelName)