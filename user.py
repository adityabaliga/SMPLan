from database import CursorFromConnectionFromPool
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, password, user_type, unit):
        self.username = username
        self.password = password
        self.user_type = user_type
        self.unit = unit



    @classmethod
    def get(cls, username):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select _password, user_type, unit from _user_ where username = %s', (username,))
            user_data = cursor.fetchone()
        if user_data:
            return cls(username, user_data[0], user_data[1], user_data[2])
        return None

    def get_id(self):
        return self.username

    def update_pwd(self,new_pwd):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('update _user_ set _password= %s where username = %s', (new_pwd,self.username))

