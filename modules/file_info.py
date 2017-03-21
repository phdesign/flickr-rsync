class FileInfo(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.checksum = kwargs.get('checksum')

