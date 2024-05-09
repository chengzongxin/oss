
class LoginModel:
    def __init__(self, dataMap: map):
        self.accountId = dataMap['accountId']
        self.uid = dataMap['uid']
        self.ticket = dataMap['ticket']


   