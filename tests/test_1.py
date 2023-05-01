import os

from aiohttp import ClientSession

from download_gitea_repository.working_file import get_list_files
from ..working_file import get_hash_file, print_hash_files, download_file, save_file


def test_get_hash_file(list_hash: list, list_files: list):
    """ Проверяет правильность рассчитывания HASH суммы по списку файлов """
    for i, item in enumerate(list_files):
        expected_hash = list_hash[i]
        calculated_hash = get_hash_file(item)
        assert expected_hash == calculated_hash


def test_print_hash_files(list_hash: list, list_files: list, capsys):
    """ Проверяет правильность отображаения рассчитанных HASH сумм списка файлов """
    comb_list = []
    for i in range(len(list_files)):
        comb_list.append(f"{list_files[i]}: {list_hash[i]}")
    expected_show = "\n".join(comb_list)
    # print(expected_show)
    print_hash_files(list_files)
    assert expected_show in capsys.readouterr().out


def sort_key(item: dict):
    return item.get("name")


async def test_get_list_files(patched_constant_url_content, list_files_params):
    """ Проверяет функцию возврата файлов из gitea репозитория """
    _dir, expected_list_files = list_files_params
    async with ClientSession() as session:
        list_files = await get_list_files(session, _dir)
        assert len(list_files) == len(expected_list_files)
        normalized_list_files = [{'name': item.get('name'), 'type': item.get('type')} for item in list_files]
        assert sorted(expected_list_files, key=sort_key) == sorted(normalized_list_files, key=sort_key)


async def test_failed_get_list_files(patched_constant_url_content, capsys):
    """
    Проверяет неудавшийся возврат файлов из gitea репозитория
    по причине отстуствия указанного каталога в репозитории
    """
    _dir = "does_not_exist_dir"
    expected_show = f'It is not possible to load a list of files from the directory gitea "{_dir}".'
    async with ClientSession() as session:
        list_files = await get_list_files(session, _dir)
        assert len(list_files) == 0
        assert expected_show in capsys.readouterr().out


async def test_download_file(tmp_path, patched_constant_url_download, fake_session):
    """ Тестирует закачку файла """
    filename = "mocks.py"
    await download_file(fake_session, filename, tmp_path)
    original_filename = os.path.join(os.getcwd(), f"download_gitea_repository/tests/{filename}")
    download_filename = os.path.join(tmp_path, filename)
    assert os.path.exists(download_filename)
    hash_original_filename = get_hash_file(original_filename)
    hash_download_filename = get_hash_file(download_filename)
    assert hash_download_filename == hash_original_filename


async def test_failed_download_file(tmp_path, patched_constant_url_download, fake_session, capsys):
    """ Тестирует неудачную закачку файла, когда такого файла не существует """
    filename = "does_not_exist_file.dat"
    await download_file(fake_session, filename, tmp_path)
    download_filename = os.path.join(tmp_path, filename)
    assert not os.path.exists(download_filename)
    expected_show = f"Unable to upload file {filename}. Response status 400."
    assert expected_show in capsys.readouterr().out


async def test_save_file(tmp_path, fake_response):
    filename = "conftest.py"
    download_filename = os.path.join(tmp_path, filename)
    await save_file(fake_response, download_filename)
    assert os.path.exists(download_filename)
    original_filename = os.path.join(os.getcwd(), f"download_gitea_repository/tests/{filename}")
    hash_original_filename = get_hash_file(original_filename)
    hash_download_filename = get_hash_file(download_filename)
    assert hash_download_filename == hash_original_filename
