def setup_storage(storage, folders):
    """
    Fakes a folder / file configuration on a storage mock. Pass a None folder as the root folder.

    Args:
        storage: A MagicMock to add mock behaviour to
        folders: A list of dictionaries of folder and file items in the format 
            [{ 'folder': FolderInfo, 'files': [FileInfo, ...] }, ...]

    Example:
        helpers.setup_storage(self.storage, [
            { 'folder': None, 'files': [] },
            { 'folder': folder_one, 'files': [file_one, file_two] }
        ])
    """
    storage.list_folders.return_value = [x['folder'] for x in folders if x['folder'] != None]
    storage.list_files.side_effect = lambda folder: next((x['files'] for x in folders if x['folder'] == folder), [])
