import os
import shutil
import logging
from filecmp import cmp


class Folder:
    """Entity representing existing directory"""
    path: str

    def __init__(self, path: str) -> None:
        """
        Creates Folder object and checks for existence

        :param path: a path to existing folder
        """
        if type(path) != str:
            raise TypeError("Path should be a string!")
        elif not os.path.isdir(path):
            raise ValueError("Given path is not a folder or does not exist")
        self.path = path

    @staticmethod
    def compare_files(file_path1: str, file_path2: str, content: bool = True) -> bool:
        """
        Comparing two files for identity. By default, files are treated as different if their sizes or contents differ

        :param file_path1: path to the first file
        :param file_path2: path to the second file
        :param content: True if content comparison is needed.
        :return: True if files are the same and False otherwise
        """
        return cmp(file_path1, file_path2, shallow=not content)

    def is_alive(self) -> bool:
        """
        Checks for folder existence

        :returns: True if folder still exists else False
        """
        return os.path.isdir(self.path)

    def revive(self) -> None:
        """
        Restores folder if it was deleted
        """
        os.mkdir(self.path)

    def remove(self, file_path: str) -> None:
        """
        Removes file or entire directory from folder

        :param file_path: path to a file or a directory in a folder
        """
        # normalizing path to remove ../ and use os separators
        file_path = os.path.normpath(file_path).strip(os.sep)
        # remove only content inside folder
        if not (file_path.startswith(self.path + os.sep) or file_path == os.path.normpath(self.path)):
            raise PermissionError(f"Can't delete a file outside of {self.path!r}")

        if os.path.isdir(file_path):
            logging.debug(f"Removing folder {file_path}")
            shutil.rmtree(file_path)
            logging.info(f"Folder {file_path!r} removed")
        else:
            logging.debug(f"Removing file {file_path}")
            os.remove(file_path)
            logging.info(f"{file_path!r} removed")

    def copy_into(self, src: str, dst: str) -> None:
        """
        Copies file or entire folder to a folder (deep copy with metadata)

        :param src: full path from source folder to a file
        :param dst: full destination path to a folder with its filename"""
        file_path = os.path.normpath(dst).strip(os.sep)
        # copy only inside the folder
        if not (file_path.startswith(self.path + os.sep) or file_path == os.path.normpath(self.path)):
            raise PermissionError(f"Can't copy a file outside of {self.path!r}")

        if not os.path.isdir(src):
            logging.debug(f"Copying {src!r} to {dst!r}")
            shutil.copy2(src, dst, follow_symlinks=False)
            logging.info(f"File {src!r} was copied")
        else:
            logging.debug(f"Copying entire folder {src!r} to {dst!r}")
            shutil.copytree(src, dst)
            logging.info(f"Folder {src!r} was copied")
