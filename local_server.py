import json
import socket
from threading import Thread

from search_and_sort_utils import *

buffer_size = 102400


def iter_search(client_socket):  # 线程执行函数
    recved = json.loads(client_socket.recv(buffer_size))  # 接收检索请求
    mode = recved[0]  # 识别检索模式
    terms = recved[1]  # 获取检索词
    news_idx_list = []
    num_words = len(terms)

    if mode == 0:  # 宽松检索
        #  优先检索包含检索词较多的新闻
        if num_words == 3:
            news_idx_list_012 = search_and_sort_by_word(terms)
            news_idx_list_01 = search_and_sort_by_word([terms[0], terms[1]])
            news_idx_list_02 = search_and_sort_by_word([terms[0], terms[2]])
            news_idx_list_12 = search_and_sort_by_word([terms[1], terms[2]])
            news_idx_list += news_idx_list_012 + news_idx_list_01 + news_idx_list_02 + news_idx_list_12
        if num_words == 2:
            news_idx_list_01 = search_and_sort_by_word(terms)
            news_idx_list += news_idx_list_01
        for word in terms:
            news_idx_list += search_and_sort_by_word(word)

    elif mode == 1:  # 严格检索
        news_idx_list += search_and_sort_by_word(terms)

    elif mode == 2:  # 模糊检索
        word = terms[0]
        synonyms_num = 2
        synonyms = get_synonyms(word, k=synonyms_num)
        news_idx_list += search_and_sort_by_word(word)
        for i in range(synonyms_num):
            news_idx_list += search_and_sort_by_word(synonyms[i])

    else:
        raise NotImplemented

    # 确保每条新闻只出现一次，而且是排序最靠前的那次
    unique_list = []
    for i in news_idx_list:
        if i not in unique_list:
            unique_list.append(i)

    # 发送检索结果
    result = json.dumps(unique_list)
    client_socket.send(bytes(result.encode('utf-8')))
    client_socket.close()

    return


class LocalServer(object):
    def __init__(self, host, port):
        self.address = (host, port)

    def run(self):
        """
        文本检索以及服务器端与客户端之间的通信（服务器多线程并发处理客户端发来的请求）
        1. 接受客户端传递的数据， 例如检索词
        2. 调用检索函数，根据检索词完成检索
        3. 将检索结果发送给客户端，具体的数据格式可以自己定义
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(self.address)

        while True:  # 循环处理请求
            server.listen(100)
            client_socket, _ = server.accept()

            t = Thread(target=iter_search, args=(client_socket,))  # 将请求交给派生线程处理
            t.start()


server_host = '127.0.0.1'
server_port = 1234

server = LocalServer(server_host, server_port)
server.run()
