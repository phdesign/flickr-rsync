from __future__ import print_function
from mock import NonCallableMock 

def setup_storage(storage, folders):
    """
    Fakes a folder / file configuration on a storage mock. Pass a None folder as the root folder.

    Args:
        storage: A MagicMock to add mock behaviour to
        folders: A list of dictionaries of folder and file items in the format 
            [{ 'folder': FolderInfo, 'files': [FileInfo, ...] }, ...]

    Example:
        helpers.setup_storage(self.storage, [
            { 'folder': RootFolderInfo(), 'files': [] },
            { 'folder': folder_one, 'files': [file_one, file_two] }
        ])
    """
    storage.list_folders.return_value = [x['folder'] for x in folders if not x['folder'].is_root]
    storage.list_files.side_effect = \
        lambda folder: next(
            (x['files'] for x in folders if x['folder'] == folder or (x['folder'].is_root and folder.is_root)), [])

def assert_has_calls_exactly(mock, calls, any_order=False):
    mock.assert_has_calls(calls, any_order=any_order)
    assert (mock.call_count == len(calls),
            "Expected '{}' to be called {} times. Called {} times.".format(mock._mock_name, mock.call_count, len(calls)))

NonCallableMock.assert_has_calls_exactly = assert_has_calls_exactly
