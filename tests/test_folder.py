import os
import shutil
import pytest

from folder import Folder


def test_folder_creation_exist():
    try:
        os.mkdir("test_folder")
    except:
        pass
    try:
        f = Folder("test_folder")
    except:
        assert False
    shutil.rmtree("test_folder")


def test_folder_creation_not_exist():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    with pytest.raises(ValueError):
        Folder("test_folder")


def test_folder_creation_wrong_path():
    with pytest.raises(TypeError):
        Folder(123)


def test_is_alive_true():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    f = Folder("test_folder")
    status = f.is_alive()
    shutil.rmtree("test_folder")
    assert status


def test_is_alive_false():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    f = Folder("test_folder")
    shutil.rmtree("test_folder")
    assert not f.is_alive()


def test_revive():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    f = Folder("test_folder")
    shutil.rmtree("test_folder")
    f.revive()
    status = f.is_alive()
    shutil.rmtree("test_folder")
    assert status


def test_compare_files_with_meta():
    with open("test_file", 'w+') as file:
        file.write("new line")
    shutil.copy2("test_file", "test_file1")
    status = Folder.compare_files("test_file", "test_file1")
    os.remove("test_file")
    os.remove("test_file1")
    assert status


def test_compare_files_without_meta():
    with open("test_file", 'w+') as file:
        file.write("new line")
    shutil.copy("test_file", "test_file1")
    status = Folder.compare_files("test_file", "test_file1")
    os.remove("test_file")
    os.remove("test_file1")
    assert status


def test_compare_files_modified():
    with open("test_file", 'w+') as file:
        file.write("new line")
    shutil.copy2("test_file", "test_file1")
    with open("test_file1", 'a') as file:
        file.write("\nappended text")
    status = not Folder.compare_files("test_file", "test_file1")
    os.remove("test_file")
    os.remove("test_file1")
    assert status


def test_remove_existing():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    with open("test_folder/test_file", 'w+') as file:
        file.write("new line")

    f = Folder("test_folder")
    f.remove("test_folder/test_file")
    status = "test_file" not in os.listdir(f.path)
    shutil.rmtree("test_folder")
    assert status


def test_remove_folder():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    try:
        os.mkdir("test_folder/inner_folder")
    except:
        pass
    with open("test_folder/inner_folder/inner_file", 'w+') as file:
        file.write("new line")

    f = Folder("test_folder")
    f.remove("test_folder/inner_folder")
    status = "inner_folder" not in os.listdir('test_folder')
    shutil.rmtree("test_folder")
    assert status


def test_remove_outside():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    try:
        shutil.rmtree("test_folder1")
    except:
        pass
    os.mkdir("test_folder1")
    with open("test_folder1/outside", 'w+') as file:
        file.write("new line")
    f = Folder("test_folder")
    with pytest.raises(PermissionError):
        f.remove("test_folder1/outside")


def test_remove_outside_similar_name():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    try:
        shutil.rmtree("test_folder1")
    except:
        pass
    os.mkdir("test_folder1")
    with open("test_folder1/outside", 'w+') as file:
        file.write("new line")
    f = Folder("test_folder")
    with pytest.raises(PermissionError):
        f.remove("test_folder1/outside")


def test_copy_into_file():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    # another folder starts with the same string
    try:
        shutil.rmtree("test_folder1")
    except:
        pass
    os.mkdir("test_folder1")
    with open("test_folder1/text", 'w+') as file:
        file.write("line of text")

    f = Folder("test_folder")
    f.copy_into("test_folder1/text", "test_folder/text")
    assert "text" in os.listdir("test_folder")


def test_copy_into_folder():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    try:
        shutil.rmtree("test_folder1")
    except:
        pass
    os.mkdir("test_folder1")
    os.mkdir("test_folder1/inner")
    with open("test_folder1/inner/text", 'w+') as file:
        file.write("line of text")

    f = Folder("test_folder")
    f.copy_into("test_folder1/inner", "test_folder/inner")
    assert "inner" in os.listdir("test_folder") and 'text' in os.listdir("test_folder/inner")


def test_copy_outside():
    try:
        shutil.rmtree("test_folder")
    except:
        pass
    os.mkdir("test_folder")
    try:
        shutil.rmtree("test_folder1")
    except:
        pass
    os.mkdir("test_folder1")
    os.mkdir("test_folder/inner")
    with open("test_folder/inner/text", 'w+') as file:
        file.write("line of text")

    f = Folder("test_folder")
    try:
        f.copy_into("test_folder/inner/", "test_folder1/inner/")
        shutil.rmtree("test_folder")
        shutil.rmtree("test_folder1")
        assert False
    except PermissionError:
        shutil.rmtree("test_folder")
        shutil.rmtree("test_folder1")
        assert True
