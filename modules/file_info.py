class FileInfo(object):

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.name = kwargs['name']
        self.checksum = kwargs['checksum']

