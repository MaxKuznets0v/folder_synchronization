from time import sleep
import argparse
import logging

from synchronizer import Synchronizer
from folder import Folder


def keep_folders_sync(synchronizer: Synchronizer, interval: int = 600) -> None:
    """
    Synchronizes folders every 'interval' seconds

    :param synchronizer: Synchronizer object for folders' sync
    :param interval: synchronization period of time in seconds (10 mins by default)
    """
    logging.debug(f"Running folders' synchronization with {interval = }")
    while True:
        logging.info("Starting synchronization")
        remove_err, update_err = synchronizer.sync_folders()
        rm_err_num = len(remove_err)
        upd_err_num = len(update_err)
        if rm_err_num + upd_err_num == 0:
            logging.info("Folders successfully synchronized!")
        else:
            info = ""
            if rm_err_num > 0:
                info += f"\nNot removed from replica ({rm_err_num}): {remove_err}"
            if upd_err_num > 0:
                info += f"\nNot updated from source ({upd_err_num}): {update_err}"
            logging.info(f"Folders synchronized partially! Failed files ({rm_err_num + upd_err_num}): {info}")
        sleep(interval)


def configure_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Synchronizing 2 folders (source and replica)')
    parser.add_argument('-s', '--source', type=str, help='path to a source folder (must exist)', required=True)
    parser.add_argument('-r', '--replica', type=str, help='path to a replica folder (must exist)', required=True)
    parser.add_argument('-i', '--interval', type=float, help='synchronization period of time in seconds', default=600)
    parser.add_argument('-l', '--log_file', type=str, help='path to a log file (creates if not exists)', default='sync.log')
    return parser.parse_args()


def configure_logger() -> None:
    fmt = '[%(levelname)s: %(asctime)s] - %(message)s'
    logging.basicConfig(format=fmt, level=logging.DEBUG, datefmt='%d.%m.%Y %H:%M:%S', filename=args.log_file,
                        encoding='utf-8')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt=logging.Formatter(fmt=fmt))
    logging.getLogger('').addHandler(console)


if __name__ == '__main__':
    args = configure_args()
    configure_logger()

    try:
        source = Folder(args.source)
    except ValueError as e:
        raise ValueError(f"{e} ({args.source!r})")
    try:
        replica = Folder(args.replica)
    except ValueError as e:
        raise ValueError(f"{e} ({args.replica!r})")

    sync = Synchronizer(source, replica)
    try:
        keep_folders_sync(sync, args.interval)
    except:
        logging.exception("Unknown error occurs", exc_info=True)
