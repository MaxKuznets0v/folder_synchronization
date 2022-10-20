import os
import shutil
import stat
import pytest

from folder import Folder
from synchronizer import Synchronizer


@pytest.fixture()
def source():
    try:
        os.mkdir("test_source")
    except:
        pass
    return Folder("test_source")


@pytest.fixture()
def replica():
    try:
        os.mkdir("test_replica")
    except:
        pass
    return Folder("test_replica")


def test__remove_obsolete_file(source, replica):
    try:
        shutil.rmtree(source.path + "/inner")
    except:
        pass
    os.mkdir(source.path + "/inner")
    try:
        shutil.rmtree(replica.path + "/inner")
    except:
        pass
    os.mkdir(replica.path + "/inner")
    with open(replica.path + "/inner/text", 'w+') as file:
        file.write("text line")

    s = Synchronizer(source, replica)
    r_path = replica.path + '/inner'
    s._remove_obsolete(set(os.listdir(source.path + "/inner")), set(os.listdir(r_path)), r_path)
    assert 'text' not in os.listdir(r_path)


def test__remove_obsolete_folder(source, replica):
    try:
        shutil.rmtree(source.path + "/inner")
    except:
        pass
    try:
        shutil.rmtree(replica.path + "/inner")
    except:
        pass
    os.mkdir(replica.path + "/inner")
    with open(replica.path + "/inner/text", 'w+') as file:
        file.write("text line")

    s = Synchronizer(source, replica)
    s._remove_obsolete(set(os.listdir(source.path)), set(os.listdir(replica.path)), replica.path)
    assert 'inner' not in os.listdir(replica.path)


def test__remove_obsolete_with_errors(source, replica):
    with open(replica.path + "/text", 'w+') as file:
        file.write("text line")
    # making a file read-only
    os.chmod(replica.path + "/text", 0o0444)
    s = Synchronizer(source, replica)
    errors = s._remove_obsolete(set(os.listdir(source.path)), set(os.listdir(replica.path)), replica.path)
    # remove read-only flag
    os.chmod(replica.path + "/text", stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
    os.remove(replica.path + "/text")
    assert os.path.normpath(replica.path + "/text") in errors and len(errors) == 1


def test__update_file_identical(source, replica):
    with open(source.path + "/text", 'w+') as file:
        file.write("text line")
    shutil.copy2(source.path + "/text", replica.path + '/text')
    with open(source.path + "/text", 'a') as file:
        file.write("\nnew line")

    s = Synchronizer(source, replica)
    s._update_file(source.path, replica.path)
    status = Folder.compare_files(source.path + "/text", replica.path + '/text')
    os.remove(source.path + "/text")
    os.remove(replica.path + '/text')
    assert status


def test__update_file_same(source, replica):
    with open(source.path + "/text", 'w+') as file:
        file.write("text line")
    with open(source.path + "/text", 'w+') as file:
        file.write("text line\nnew line")
    with open(source.path + "/text", 'a') as file:
        file.write("\nnew line")

    s = Synchronizer(source, replica)
    s._update_file(source.path, replica.path)
    status = Folder.compare_files(source.path + "/text", replica.path + '/text')
    os.remove(source.path + "/text")
    os.remove(replica.path + '/text')
    assert status


def test__update_folder(source, replica):
    try:
        shutil.rmtree(source.path + "/inner")
    except:
        pass
    os.mkdir(source.path + "/inner")
    try:
        shutil.rmtree(replica.path + "/inner")
    except:
        pass
    os.mkdir(replica.path + "/inner")

    with open(source.path + "/inner/text", 'w+') as file:
        file.write("text line")
    s = Synchronizer(source, replica)
    s._update_file(source.path, replica.path)
    status = 'text' in os.listdir(replica.path + "/inner")

    # cleaning up
    shutil.rmtree(source.path + "/inner")
    shutil.rmtree(replica.path + "/inner")
    assert status


def test_sync_folders_obsolete_new_modified(source, replica):
    try:
        shutil.rmtree(source.path + "/inner")
    except:
        pass
    os.mkdir(source.path + "/inner")
    try:
        shutil.rmtree(replica.path + "/inner")
    except:
        pass
    os.mkdir(replica.path + "/inner")
    # new file
    with open(source.path + "/inner/new", 'w+') as file:
        file.write("new file")

    # modified file
    with open(source.path + "/inner/modified", 'w+') as file:
        file.write("old line")
    shutil.copy2(source.path + "/inner/modified", replica.path + "/inner/modified")
    with open(source.path + "/inner/modified", 'a+') as file:
        file.write("\nnew line")

    # obsolete file
    with open(replica.path + '/obsolete', 'w+') as file:
        file.write('obsolete line')

    s = Synchronizer(source, replica)
    s.sync_folders()
    status = 'obsolete' not in os.listdir(replica.path) and 'new' in os.listdir(replica.path + '/inner')
    status = status and Folder.compare_files(source.path + "/inner/modified", replica.path + "/inner/modified")
    shutil.rmtree(source.path + "/inner")
    shutil.rmtree(replica.path + "/inner")

    assert status


def test_sync_folders_new_folder(source, replica):
    try:
        shutil.rmtree(source.path + "/inner")
    except:
        pass
    os.mkdir(source.path + "/inner")

    with open(source.path + "/inner/new1", 'w+') as file:
        file.write("file1")
    with open(source.path + "/inner/new2", 'w+') as file:
        file.write("file2")
    with open(source.path + "/inner/new3", 'w+') as file:
        file.write("file3")

    s = Synchronizer(source, replica)
    s.sync_folders()

    status = 'inner' in os.listdir(replica.path) and {'new1', 'new2', 'new3'} == set(os.listdir(replica.path + '/inner'))
    shutil.rmtree(source.path + "/inner")
    shutil.rmtree(replica.path + "/inner")
    shutil.rmtree(source.path)
    shutil.rmtree(replica.path)
    assert status
