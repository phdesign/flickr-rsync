class FolderInfo(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.full_path = kwargs.get('full_path')

    def __repr__(self):
        return "FolderInfo: {{id={}, name={}}}".format(self.id, self.name)
