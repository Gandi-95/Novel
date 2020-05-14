import sys
import getopt
import os
import requests
import time
from lxml import etree

url = 'http://192.168.1.103:5000/fabfile/ime-fabfile/task/searchlogs/execute_search'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept - Encoding': 'gzip, deflate',
    'Accept - Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Length': '110',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': '192.168.1.103:5000',
    'Origin': 'http://192.168.1.103:5000',
    'Referer': 'http://192.168.1.103:5000/fabfile/ime-fabfile/task/searchlogs/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

header = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
}


def main(argv):
    search_time = time.strftime("%Y-%m-%d %H", time.localtime(time.time()))

    imei = '352912030593065'
    dstr_st = search_time
    dstr_end = search_time
    keyword = 'event'
    try:
        opts, args = getopt.getopt(argv[1:], "hi:s:e:k:", ["imei=", "start_time=", "end_time=", "keyword="])
    except getopt.GetoptError:
        print('usage: python [option] ... [-i <imei> -s <start_time> -e <end_time> -k <keyword>]')
        sys.exit(2)

    if len(opts) < 1:
        print('usage: python [option] ... [-i <imei>]')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('usage: python [option] ... [-i <imei> -s <start_time> -e <end_time> -k <keyword>]')
            sys.exit()
        elif opt in ("-i", "--imei"):
            imei = arg
            print("imei:"+imei)
        elif opt in ("-s", "--start_time"):
            dstr_st = arg
            print("start_time:" + dstr_st)
        elif opt in ("-e", "--end_time"):
            dstr_end = arg
            print("end_time:" + dstr_end)
        elif opt in ("-k", "--keyword"):
            keyword = arg
            print("keyword:" + keyword)


    data = {'company_select': 'ime',
            'imei': imei,
            'dstr_st': dstr_st,
            'dstr_end': dstr_end,
            'keyword': keyword,
            'keyword_manul': ''}

    response = requests.post(url, data=data, headers=headers)
    etree_html = etree.HTML(response.text)
    text = etree_html.xpath('/html/body/div/pre/font/text()')
    lines = text[0].split('\n')

    name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
    log_path = os.getcwd() + "/searchlogs/"
    if not os.path.exists(log_path):
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(log_path)

    log_name = log_path + name + ".log"
    print("log_name:"+log_name)
    with open(log_name,"a",encoding='gb18030') as f:
        for line in lines:
            line = line.rstrip('\r')
            f.write(line+"\n")



if __name__ == '__main__':
    main(sys.argv)

