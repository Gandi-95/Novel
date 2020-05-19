import websocket
import threading
import random
import queue
import logging
import time
import sys
import requests
import http.cookiejar as HC
import json
from Logger import Logger

headers = {
    'Accept - Encoding': 'gzip, deflate, br',
    'Accept - Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'Upgrade',
    'Host': 'cca1.szime.com',
    'Origin': 'http://cca2.szime.com',
    'Pragma': 'no-cache',
    'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    'Sec-WebSocket-Key': 'QWYbqy6iPWb2R7/ZZFafGw==',
    'Sec-WebSocket-Protocol': 'imp.1.json',
    'Sec-WebSocket-Version': '13',
    'Upgrade': 'websocket',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

cookie_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'cca2.szime.com',
    'Referer': 'http://edog.szime.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
}

json_headers = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'cca2.szime.com',
    'Referer': 'http://cca2.szime.com/home',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

count = 0;
q = queue.Queue()
logger = Logger(name="imeClient")

imei = ''
prot = 'new'
token = ''


# 发送token，保持长连接
def keep_connect(ws):
    global count
    first_connect = '[2, %i, {"token": "%s"}]' % (count, token)
    sendMsg(ws, first_connect)
    time.sleep(3)
    while True:
        time.sleep(3)
        count += 1
        sendMsg(ws, '[0,' + str(count) + ',1]')


# 接受到inputCmd,发送给ime
def shellSend(ws):
    global count
    global q
    global imei
    global prot

    logger.info(">已连接到imei:" + imei + "\n")
    while True:
        if not q.empty():
            cmd = q.get()
            if cmd == 'old' or cmd == 'new':
                prot = cmd
                logger.info(">已切换" + prot + "协议\n")
            elif 'setimei:' in cmd:
                imei = cmd.strip('setimei:')
                logger.info(">已切换到imei:" + imei + "\n")
            elif 'close' in cmd:
                ws.close()
            else:
                logger.info(imei + " " + prot + " > " + cmd + "\n")
                if prot == 'new':
                    sendMsg(ws, shellStr(cmd))
                else:
                    sendMsg(ws, oldShellStr(cmd))


def oldShellStr(cmd):
    # [5,13,["u.oldmsg",["35291202045926","ls -l"]]]
    return '[5,%i,["u.oldmsg",["%s","%s"]]]' % (count, imei, cmd)


# 组合新协议发送个ime的数据
def shellStr(cmd):
    # [4,11,["427520f4-c233-9a6b-5dee-7da880525dbc",["35291202045926#0"],8,1587225923885,["shell","ls"]]]
    return '[4, %i, ["%s", ["%s#0"], 8, %i, ["shell", "%s"]]]' % (count, getUid(), imei, gettime(), cmd)


def sendMsg(ws, data):
    logger.debug("↑ : " + data)
    ws.send(data)


# 获取时间戳
def gettime():
    return int(round(time.time() * 1000))


# 随机生成UID
def getUid():
    return S4() + S4() + "-" + S4() + "-" + S4() + "-" + S4() + "-" + S4() + S4() + S4();


# 随机生成32位
def S4():
    return str(hex(random.randint(0x1000, 0xffff)))[2:]


# open IME websocket 启动保持连接线程，启动接受inputCmd线程
def on_open(ws):
    logger.debug("on_open")
    thread_test = threading.Thread(target=keep_connect, args=(ws,))
    thread_test.start()

    thread_shell = threading.Thread(target=shellSend, args=(ws,))
    thread_shell.start()


# 接收 IME 服务器返回的数据
def on_message(ws, message):
    logger.debug("↓ : " + message)
    global prot

    messages = message.strip("[]").split(',')
    try:
        type = int(messages[0])
        # 新协议type = 4 ,为 cmd 命令的返回 | 老协议为type = 1 ,数据长度为4，保持长连接的返回也是type = 1,但是数据长度为3
        if type == 4:
            result = ''.join(messages[8:])
            msg = result.strip('""').replace("\\r\\n", "\n")
            logger.info(msg)
        elif type == 1 and len(messages) > 3 and prot == 'old':
            result = ''.join(messages[3:])
            msg = result.strip('""').replace("\\n", "\n")
            logger.info(msg)
        else:
            pass
    except:
        pass


def on_error(ws, error):
    logger.debug("on_error : " + error)


def on_close(ws):
    logging.debug("on_close")


# 启动连接IME websocket
def ime_client():
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://cca1.szime.com/imclient?access_token=%s" % (token),
                                header=headers,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = on_open
    ws.run_forever()


# 接收到input的消息，添加到队列
def on_input_message(ws, message):
    global q
    q.put(message)
    logger.debug('on_input_message:' + message)


def on_input_error(ws, error):
    logger.debug("on_input_error")


def on_input_close(ws):
    logger.debug("on_input_close")


# 启动连接input 服务
def connectInput():
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:8131/",
                                header=headers,
                                on_message=on_input_message,
                                on_error=on_input_error,
                                on_close=on_input_close)

    ws.run_forever()


def get_session():
    session = requests.session()
    session.cookies = HC.LWPCookieJar(filename='cookies')
    #  如果存在cookies文件，则加载，如果不存在则提示
    try:
        session.cookies.load(ignore_discard=True)
    except:
        get_cookie(session)
    return session


# 获取cookie
def get_cookie(session):
    cookie_url = 'http://cca2.szime.com/redir?lc=zh_CN&access_token=%s&auth=http://edog.szime.com/frame_loginime?locale=zh_CN' % (
        token)
    # requests自动重定向了, 且重定向后的返回没有cookie,allow_redirects=False 禁止自动重定向
    r = session.get(cookie_url, headers=cookie_headers, allow_redirects=False)
    session.cookies.save(ignore_discard=True, ignore_expires=True)


# 获取当前imei设备版本号
def get_fwver(imei):
    session = get_session()

    # c3ngk5m38twx1sw3iswxxdmtr
    url = 'http://cca2.szime.com/api/device?_dc=1589458268639&did=%s&group=&user=&page=1&start=0&limit=60' % (imei)
    r = session.get(url, headers=json_headers)
    version_info = json.loads(r.text)
    version = version_info['items'][0]['stats']['fwver']
    logger.info(version)

    query_group(imei)


def query_group(imei):
    session = get_session()
    url = 'http://cca2.szime.com/api/user/query?q=%s&_dc=%d' % (imei, gettime())
    r = session.get(url, headers=json_headers)
    group_info = json.loads(r.text)
    group_info[0].split("\\/")


    logger.info(group_info[0].split("/"))


def get_apiServer(group_name, group):
    url = 'http://cca2.szime.com/api/user/group/%s/users?_dc=%d&query=%s&page=1&limit=30' % (
    group_name, gettime(), group)
    session = get_session()
    r = session.get(url, headers=json_headers)
    logger.info(r.text)

    '''
    {total:1,items:[{"uid":"edogtest","enabled":true,"wid":null,"locale":"en_US","attr":{"grade":1,"prefermap":"AMap"},"registerTime":1354675710654,"info":"","id":"595527800abaa3455ae2ec84","balance":0.000000,"apiServer":"cca1.szime.com:80","email":"edogtest@edog.net.cn","roles":[{"name":"AGENT_USER","permissions":[]},{"name":"DATA_ADMIN","permissions":[]},{"name":"CARD_ADMIN","permissions":[]},{"name":"TRACKER_USER","permissions":[]},{"name":"USER_ADMIN","permissions":[]},{"name":"GROUP_ADMIN","permissions":[]},{"name":"USER","permissions":["USER_READ"]}],"login":"edogtest","group":"edogtest"}]}
    '''


if __name__ == '__main__':
    if len(sys.argv) > 2:
        imei = sys.argv[1]
        token = sys.argv[2]

    logger.debug("imei:" + imei + " token:" + token)

    get_fwver(imei)

    ime_client = threading.Thread(target=ime_client)
    ime_client.start()

    inputclient = threading.Thread(target=connectInput)
    inputclient.start()

    # subprocess.Popen('python searchlogs.py', shell=True)
    # subprocess.Popen('cmd.exe /C tcping -t 192.168.88.2', creationflags=subprocess.CREATE_NEW_CONSOLE)
