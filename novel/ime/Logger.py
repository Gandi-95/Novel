import logging
import os.path
import time

class Logger(object):
    def __init__(self, name):
        """
        指定保存日志的文件路径，日志级别，以及调用文件
        将日志存入到指定的文件中
        :param name:  定义对应的程序模块名name，默认为root
        """
        # 创建一个logger
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel(logging.DEBUG)  # 指定最低的日志级别 critical > error > warning > info > debug

        # 创建一个handler，用于写入日志文件
        rq = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
        log_path = os.path.abspath(os.path.dirname(__file__)) + "/logs/"
        if not os.path.exists(log_path):
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(log_path)

        log_name = log_path + rq + ".log"
        #  这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志，解决重复打印的问题
        # if not self.logger.handlers:
        # 创建一个handler，用于输出到文件
        fh = logging.FileHandler(log_name,encoding="utf-8")
        fh.setLevel(logging.DEBUG)

        # 创建一个handler，用于输出到控制台
        # ch = logging.StreamHandler(sys.stdout)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 定义handler的输出格式
        formatterfh = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s")
        formatterch = logging.Formatter("%(message)s")
        ch.setFormatter(formatterch)
        fh.setFormatter(formatterfh)


        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def debug(self, msg):
        """
        定义输出的颜色debug--white，info--green，warning/error/critical--red
        :param msg: 输出的log文字
        :return:
        """
        # self.logger.debug(Fore.WHITE + "DEBUG - " + str(msg) + Style.RESET_ALL)
        self.logger.debug(str(msg))

    def info(self, msg):
        # self.logger.info(Fore.GREEN + "INFO - " + str(msg) + Style.RESET_ALL)
        self.logger.info(str(msg) )

    def warning(self, msg):
        # self.logger.warning(Fore.RED + "WARNING - " + str(msg) + Style.RESET_ALL)
        self.logger.warning(str(msg))

    def error(self, msg):
        # self.logger.error(Fore.RED + "ERROR - " + str(msg) + Style.RESET_ALL)
        self.logger.error(str(msg))

    def critical(self, msg):
        # self.logger.critical(Fore.RED + "CRITICAL - " + str(msg) + Style.RESET_ALL)
        self.logger.critical(str(msg))
