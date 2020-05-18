import threading
import sys
import requests
import subprocess
from lxml import etree
from websocket_server import WebsocketServer
from io import BytesIO
from PIL import Image
import os
import json
import getopt

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'JSESSIONID=1bymipqxfktlvw54yty5s53k8',
    'Host': 'edog.szime.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
}

code_headers = {
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'JSESSIONID=1bymipqxfktlvw54yty5s53k8',
    'Host': 'edog.szime.com',
    'Referer': 'http://edog.szime.com/frame_loginime?locale=zh_CN',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
}

cookie_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'cca2.szime.com',
    'Referer': 'http://edog.szime.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'
}

JSESSIONID = 'JSESSIONID='

connect = False


def keepInput(server):
    global connect
    while connect:
        cmd = input("> : ")
        server.send_message_to_all(cmd)


# 启动和imeClient连接的socket服务
def serverStart():
    server = WebsocketServer(8131, "127.0.0.1")
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()


# 当新的客户端连接时会提示
def new_client(client, server):
    global connect
    connect = True
    thread_test = threading.Thread(target=keepInput, args=(server,))
    thread_test.start()


# 当旧的客户端离开
def client_left(client, server):
    global connect
    connect = False
    print("客户端%s断开" % client['id'])


# 接收客户端的信息。
def message_received(client, server, message):
    pass


# 启动连接imeClient,py ,并传递imei
def imeClientStart(imei, itoken, sessionid):
    bash = 'python %s\imeClient.py %s %s %s' % (os.path.abspath(os.path.dirname(__file__)), imei, itoken, sessionid)
    print(bash)
    # subprocess.call(bash, creationflags=subprocess.CREATE_NEW_CONSOLE)


def main(argv):
    # python D:/PythonProjects/Novel/novel/ime/inputCmd.py -i 35291203059306
    imei = '35291203059306'

    username = 'gandii'
    password = "gand_999"
    # try:
    #     opts, args = getopt.getopt(argv[1:], "hi:s:e:k:", ["imei=", "username=", "password="])
    # except getopt.GetoptError:
    #     print('usage: python [option] ... [-i <imei> -u <username> -p <password>]')
    #     sys.exit(2)
    #
    # if len(opts) < 1:
    #     # imei = input("请输入Imei:")
    #     pass
    # else:
    #     for opt, arg in opts:
    #         if opt == '-h':
    #             print('usage: python [option] ... [-i <imei> -u <username> -p <password>')
    #             sys.exit()
    #         elif opt in ("-i", "--imei"):
    #             imei = arg
    #         elif opt in ("-u", "--username"):
    #             username = arg
    #         elif opt in ("-p", "--password"):
    #             password = arg

    itoken, cookie = login(username, password)

    server = threading.Thread(target=serverStart)
    server.start()

    cmd = threading.Thread(target=imeClientStart, args=(imei, itoken, cookie))
    cmd.start()


url = 'http://edog.szime.com/'
login_url = url + 'frame_loginime?locale=zh_CN'
token_url = url + 'oauth/token'


def token(client_secret, scope, sessionid, username, password, verify):
    data = {'grant_type': 'web',
            'client_id': 'web',
            'client_secret': client_secret,
            'scope': scope,
            'sessionid': sessionid,
            'username': username,
            'password': password,
            'verify': verify
            }
    headers['Cookie'] = JSESSIONID + sessionid
    response = requests.post(token_url, data=data, headers=headers)
    token_data = json.loads(response.text)
    if "access_token" in token_data:
        itoken = token_data['access_token'];
        print("已登录")
    else:
        print("token:" + token_data['error_description'])
        return login(username, password)

    cookie = getcookie(itoken)

    return itoken, cookie


def show_capt(capt):
    capt.show()


def login(username, password):
    response = requests.get(login_url, headers=headers)
    etree_html = etree.HTML(response.text)
    client_secret = etree_html.xpath('/html/body/div/div/div[1]/div/div/form/input[3]/@value')[0]
    scope = etree_html.xpath('/html/body/div/div/div[1]/div/div/form/input[4]/@value')[0]
    sessionid = etree_html.xpath('/html/body/div/div/div[1]/div/div/form/input[5]/@value')[0]
    verify_src = etree_html.xpath('/html/body/div/div/div[1]/div/div/form/div[3]/img/@src')[0]

    code_headers['Cookie'] = JSESSIONID + sessionid
    verify_response = requests.get(url + verify_src, headers=code_headers)
    # 将二进制的验证码图片写入IO流
    f = BytesIO(verify_response.content)
    # 将验证码转换为Image对象
    capt = Image.open(f)

    show_capt_thread = threading.Thread(target=show_capt, args=(capt,))
    show_capt_thread.start()

    verify = input('请输入验证码：')
    return token(client_secret, scope, sessionid, username, password, verify)


fwver_headers = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'JSESSIONID=1479v0m37bszk1bfpv4q3vu2i7',
    'Host': 'cca2.szime.com',
    'Referer': 'http://cca2.szime.com/home',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}


def getcookie(itoken):
    # cookie_url = 'http://cca2.szime.com/redir?lc=zh_CN&access_token=%s&auth=http://edog.szime.com/frame_loginime?locale=zh_CN' % (token)
    cookie_url = 'http://cca2.szime.com/redir?lc=zh_CN&access_token='+itoken+'&auth=http://edog.szime.com/frame_loginime?locale=zh_CN'
    print(cookie_url)
    # requests自动重定向了, 且重定向后的返回没有cookie,allow_redirects=False 禁止自动重定向
    r = requests.get(cookie_url, headers=cookie_headers, allow_redirects=False)
    print(r.headers)


    cookie = r.headers['Set-Cookie'].split(';')[1]
    print(cookie)
    getfwver('35291203059306', cookie)

    return cookie


def getfwver(imei, cookie):
    url = 'http://cca2.szime.com/api/device?_dc=1589458268639&did=%s&group=&user=&page=1&start=0&limit=60' % (imei)
    fwver_headers['Cookie'] = JSESSIONID + cookie
    r = requests.get(url, headers=fwver_headers)
    print(r.text)


if __name__ == '__main__':
    main(sys.argv)
