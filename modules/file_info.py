class FileInfo(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.full_path = kwargs.get('full_path')
        self.checksum = kwargs.get('checksum')

