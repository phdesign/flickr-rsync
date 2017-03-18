from storage import Storage
from flickr_api.objects import Photoset, Photo, Info

class SampleStorage(Storage):
    
    def __init__(self, config):
        pass

    def list_folders(self):
        folders = [
            Photoset(id=1, title="abc"),
            Photoset(id=2, title="def")
        ]
        return folders

    def list_files(self, folder):
        files = [Photo(id='32876603880', title='IMG_2131'), Photo(id='32416116504', title='IMG_2132'), Photo(id='33218094626', title='IMG_2133'), Photo(id='33259489725', title='IMG_2134'), Photo(id='33218074946', title='IMG_2135'), Photo(id='32444976173', title='IMG_2136'), Photo(id='33131097571', title='IMG_2137'), Photo(id='33103597842', title='IMG_2138'), Photo(id='33131077441', title='IMG_2139')];Info(page=1, perpage=500, pages=1, total=9)
        return files
