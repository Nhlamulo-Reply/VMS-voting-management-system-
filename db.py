import  mysql.connector
from mysql.connector import errorcode

class Database:
    def __init__(self,host,user,password,database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = mysql.connector.connect()