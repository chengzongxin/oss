
class SignatureModel:
    def __init__(self, dataMap: map):
        self.accessId = dataMap['accessId']
        self.signature = dataMap['signature']
        self.expire = dataMap['expire']
        self.host = dataMap['host']
        self.dir = dataMap['dir']
        self.policy = dataMap['policy']

        data  = dataMap['data']
        if ('newPath' in data):
            self.newPath = data['newPath']
        if ('headMap' in data and  isinstance( data['headMap'], dict)):
            self.headMap = data['headMap']
            if ('Content-Type' in self.headMap and 'x-oss-content-type' in self.headMap == False):
                self.headMap['x-oss-content-type'] = self.headMap['Content-Type']


   