# -*- coding: utf-8 -*-
import tiny_socket

class ProxyRPC:
    host = ''
    port = 0
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        
    def db_list(self):
        self.socket = tiny_socket.mysocket()
        self.socket.mysend(('db', 'list'))
        dbs = self.socket.myreceive()
        self.socket.disconnect()
        return dbs
    
    def send(self, *args):
        socket = tiny_socket.mysocket()
        socket.mysend(args)
        res = socket.myreceive()
        return res
    
    def disconnect(self):
        self.socket.disconnect()