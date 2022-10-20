import os
import logging

from folder import Folder


class Synchronizer:
    """Keeps track of folders' changes and synchronizes them"""
    source: Folder
    replica: Folder

    def __init__(self, source: Folder, replica: Folder) -> None:
        """
        :param source: folder with initial files
        :param replica: intended copy of source folder
        """
        logging.debug(f"Initializing synchronizer with {source.path = }; {replica.path = }")
        self.source = source
        self.replica = replica

    def _remove_obsolete(self, s_files: set, r_files: set, r_base: str) -> list[str]:
        """
        Removes files and folders (non recursively) from current replica folder if it's not found in source folder

        :param s_files: list of file names in current source folder
        :param r_files: list of file names in current replica folder
        :param r_base: path to a current replica folder
        :returns: a list of file paths those could not be deleted
        """
        to_delete = r_files - s_files
        remove_errors = list()

        if len(to_delete) > 0:
            logging.info(f"Found {len(to_delete)} obsolete file(s)")
        for file in to_delete:
            try:
                self.replica.remove(os.path.join(r_base, file))
            except:
                logging.exception("Could not remove file")
                remove_errors.append(os.path.join(r_base, file))

        return remove_errors

    def _update_file(self, source_path: str, replica_path: str) -> tuple[list, list] | None:
        """
        Updates existing file if its content differs from source file. It calls sync_folders method if file is a folder

        :param source_path: path of a file in source folder
        :param replica_path: path of a file in replica folder
        :returns: a list of current failed to remove files and a list of current failed to copy files
        """
        # if it's an existing folder recursively synchronize
        if os.path.isdir(source_path):
            return self.sync_folders(source_path, replica_path)
        else:
            # if it's an existing file check for changes and copy if it's needed
            if not Folder.compare_files(source_path, replica_path):
                logging.debug(f"Updating {source_path!r} from source")
                self.replica.copy_into(source_path, replica_path)
                logging.info(f"File {source_path!r} updated from source")

    def sync_folders(self, s_base: str = None, r_base: str = None) -> tuple[list, list]:
        """
        Recursively synchronizes source folder with replica.

        :param s_base: path to a current folder in source
        :param r_base: path to a current folder in replica
        :returns: a list of failed to remove files and a list of failed to copy files
        """
        if not self.source.is_alive():
            msg = "Source folder was removed during runtime"
            logging.critical(msg)
            raise RuntimeError(msg)
        # if replica folder is removed while running for some reason => create new and sync again
        if not self.replica.is_alive():
            logging.error("Replica folder was removed during runtime. Trying to resync..")
            self.replica.revive()
            return self.sync_folders()

        s_base = s_base if s_base is not None else self.source.path
        r_base = r_base if r_base is not None else self.replica.path
        s_files = set(os.listdir(s_base))
        r_files = set(os.listdir(r_base))

        update_errors = list()

        # keep track of removed files
        remove_errors = self._remove_obsolete(s_files, r_files, r_base)

        # keep track of new and updated files
        for file in s_files:
            s_full_file = os.path.join(s_base, file)
            if file in r_files:
                try:
                    upd_res = self._update_file(s_full_file, os.path.join(r_base, file))
                    if upd_res is not None:
                        remove_errors.extend(upd_res[0])
                        update_errors.extend(upd_res[1])
                except:
                    logging.exception("Could not update a file!")
                    update_errors.append(s_full_file)
            else:
                try:
                    # if new file created in source
                    self.replica.copy_into(s_full_file, os.path.join(r_base, file))
                except:
                    logging.exception("Could not copy a file!")
                    update_errors.append(s_full_file)

        return remove_errors, update_errors
