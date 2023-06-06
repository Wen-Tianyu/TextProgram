import tkinter as tk
import socket
import json
import pandas as pd

server_host = '127.0.0.1'
server_port = 1234

buffer_size = 102400


class MainPanel:
    def __init__(self, host, port):
        """
        连接服务器
        :param host: 服务器主机号
        :param port: 服务器端口号
        """
        self.addr = (host, port)
        self.documents = ...
        self.root = ...
        self.label = ...
        self.new_searchterm_entry = ...
        self.confirm_button = ...
        self.hint_label = ...
        self.title_tk = ...
        self.scrollbar = ...
        self.listbox = ...

    def start(self):
        """
        显示文本检索主界面
        """
        self.root = tk.Tk()
        self.root.geometry('400x400')
        self.root.title("文本检索")
        self.label = tk.Label(self.root, text="请输入检索词，用空格分隔:", font=(None, 12)).pack(pady=40)

        self.new_searchterm_entry = tk.Entry(self.root, font=(None, 12))
        self.new_searchterm_entry.pack()
        self.confirm_button_0 = tk.Button(self.root, text=" 宽松检索:  出现任意词即可 ", font=(None, 12),
                                          command=self.check_new_searchterm_0).pack(pady=15)
        self.confirm_button_1 = tk.Button(self.root, text=" 严格检索:  所有词同时出现 ", font=(None, 12),
                                          command=self.check_new_searchterm_1).pack(pady=15)
        self.confirm_button_2 = tk.Button(self.root, text="模糊检索: 出现该词或其相似词", font=(None, 12),
                                          command=self.check_new_searchterm_2).pack(pady=15)

        self.hint_label = tk.Label(self.root, text="", font=(None, 12))
        self.hint_label.pack()

        self.root.mainloop()

    def check_new_searchterm_0(self):
        """
        用户点击"确认"按钮后，检查输入是否合法
        """
        searchterm = self.new_searchterm_entry.get()
        terms = searchterm.split(' ')
        terms = [i for i in terms if i != '']
        if len(terms) == 0 or len(terms) > 3:
            self.hint_label.config(text=f"请输入1-3个检索词")
        else:
            self.search_request_0(terms)

    def check_new_searchterm_1(self):
        """
        用户点击"确认"按钮后，检查输入是否合法
        """
        searchterm = self.new_searchterm_entry.get()
        terms = searchterm.split(' ')
        terms = [i for i in terms if i != '']
        if len(terms) == 0 or len(terms) > 3:
            self.hint_label.config(text=f"请输入1-3个检索词")
        else:
            self.search_request_1(terms)

    def check_new_searchterm_2(self):
        """
        用户点击"确认"按钮后，检查输入是否合法
        """
        searchterm = self.new_searchterm_entry.get()
        terms = searchterm.split(' ')
        terms = [i for i in terms if i != '']
        if len(terms) == 0 or len(terms) > 1:
            self.hint_label.config(text=f"请输入1个检索词")
        else:
            self.search_request_2(terms)

    def search_request_0(self, terms):  # 宽松检索（其他两种检索同理）
        """
        实现客户端与服务器端的通信
        1. 向服务器发送检索词
        2. 接受服务器返回的检索结果
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))

        # 发送检索请求
        terms = json.dumps([0, terms])
        client_socket.send(bytes(terms.encode('utf-8')))

        # 接收检索结果
        result = json.loads(client_socket.recv(buffer_size))

        # 本地获取对应新闻标题和内容（如果直接传输内容过大）
        df = pd.read_csv('./all_news.csv')
        self.documents = []
        for idx in result:
            row = df.iloc[idx, :]
            self.documents.append(tuple([row['title'], row['body']]))

        # 展示检索结果
        self.show_titles()

    def search_request_1(self, terms):  # 严格检索
        """
        实现客户端与服务器端的通信
        1. 向服务器发送检索词
        2. 接受服务器返回的检索结果
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))

        terms = json.dumps([1, terms])
        client_socket.send(bytes(terms.encode('utf-8')))

        result = json.loads(client_socket.recv(buffer_size))

        df = pd.read_csv('./all_news.csv')
        self.documents = []
        for idx in result:
            row = df.iloc[idx, :]
            self.documents.append(tuple([row['title'], row['body']]))

        # 展示检索结果
        self.show_titles()

    def search_request_2(self, terms):  # 模糊检索
        """
        实现客户端与服务器端的通信
        1. 向服务器发送检索词
        2. 接受服务器返回的检索结果
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))

        terms = json.dumps([2, terms])
        client_socket.send(bytes(terms.encode('utf-8')))

        result = json.loads(client_socket.recv(buffer_size))

        df = pd.read_csv('./all_news.csv')
        self.documents = []
        for idx in result:
            row = df.iloc[idx, :]
            self.documents.append(tuple([row['title'], row['body']]))

        # 新闻去重
        unique_list = []
        for i in self.documents:
            if i not in unique_list:
                unique_list.append(i)
        self.documents = unique_list

        # 展示检索结果
        self.show_titles()

    def show_titles(self):
        """
        显示所有相关的文章
        1. 显示根据检索词搜索到的所有文章标题，使用滚动条显示（tkinter的Scrollbar控件）
        2. 点击标题，显示文章的具体内容（这里使用了 Listbox 控件的bind方法，动作为 <ListboxSelect>)
        """
        self.title_tk = tk.Tk()
        self.title_tk.geometry("300x300")
        self.title_tk.title("检索结果")
        self.show_listbox(self.title_tk, self.documents)

    def show_listbox(self, title_tk, documents):
        self.scrollbar = tk.Scrollbar(title_tk)
        self.scrollbar.pack(side='right', fill='both')
        self.listbox = tk.Listbox(title_tk, yscrollcommand=self.scrollbar.set, font=(None, 12))

        for doc in documents:
            self.listbox.insert("end", str(doc[0]))
        self.listbox.bind('<<ListboxSelect>>', self.show_content(documents))
        self.listbox.pack(side='left', fill='both', expand=True)

    def show_content(self, documents):
        """
        显示文档的具体内容
        """

        def callback(event):
            idx = event.widget.curselection()[0]
            content_tk = tk.Tk()
            content_tk.geometry("300x300")
            content_tk.title("显示全文")
            # print(self.documents[idx])
            text = tk.Text(content_tk, font=(None, 12))
            text.config(spacing1=10)  # 调整一下行间距
            text.config(spacing2=5)
            for item in documents[idx]:
                text.insert("end", str(item) + '\n')
            text["state"] = 'disabled'
            text.pack()

        return callback

    def reset(self):
        self.__init__(self.addr[0], self.addr[1])
        self.start()


if __name__ == "__main__":
    gui = MainPanel(server_host, server_port)
    gui.start()
