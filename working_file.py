"""
Test task

Downloads all files from the Gitea repository asynchronously
and then calculates the HASH sum of each file
"""

import asyncio
import os
from hashlib import sha256
from http import HTTPStatus
from tempfile import TemporaryDirectory
from typing import Final

import aiofiles
from aiohttp import ClientSession, ClientResponse

GITEA_DOMAIN: Final = "https://gitea.radium.group"
REPOSITORY: Final = "radium/project-configuration"
URL: Final = fr"{GITEA_DOMAIN}/{REPOSITORY}"
URL_CONTENT: Final = f"{GITEA_DOMAIN}/api/v1/repos/{REPOSITORY}/contents/"
URL_DOWNLOAD: Final = f"{URL}/raw/branch/master/"

file_list = []


async def create_tasks_download_files(
        session: ClientSession, tasks: list, _file_list: list, _dir: str):
    """
    Формирует список задач по асинхронной загрузке файлов
    :param session: сессия
    :param tasks: список асинхронных задач
    :param _file_list: список файлов и деректориев gitea
    :param _dir: директорий в который должны быть загружены файлы
    :return:
    """
    for file in _file_list:
        file_name = file.get("path")
        if file.get("type") == "file":
            # print("Download file: " + file_name)
            tasks.append(asyncio.create_task(
                download_file(session, file_name, _dir)))
        elif file.get("type") == "dir":
            dir_name = os.path.join(_dir, file_name)
            os.makedirs(dir_name)
            await create_tasks_download_files(
                session,
                tasks,
                await get_list_files(session, file.get("path")), dir_name)


def check_response_status(response: ClientResponse):
    """ Проверят статус ответа """
    if response.status != HTTPStatus.OK:
        raise ConnectionError(f"Ошибка ответа. Код {response.status}")


async def download_file(session: ClientSession, file_name: str, _dir: str):
    """
    Загружает файл

    :param session: сессия
    :param file_name: имя файла с путем в gitea
    :param _dir: директорий на диске куда должен быть загружен файл
    :return:
    """
    async with session.get(URL_DOWNLOAD + file_name) as response:
        try:
            check_response_status(response)
            temp_dir_file_name = os.path.join(_dir, os.path.basename(file_name))
            await save_file(response, temp_dir_file_name)
        except ConnectionError:
            print(f"Unable to upload file {file_name}. Response status {response.status}.")


async def save_file(response: ClientResponse, file_name: str):
    """
    Сохраняет файл

    :param response: ответ
    :param file_name: полное имя сохраняемого файла
    :return:
    """
    async with aiofiles.open(file_name, 'wb') as file:
        # print("Write file: " + file_name)
        file_list.append(file_name)
        await file.write(await response.content.read())


async def get_list_files(session: ClientSession, path_dir: str = ""):
    """
    Возвращает список файлов по указанному пути gitea

    :param session: сессия
    :param path_dir: каталог в gitea из которого надо вернуть список файлов
    :return:
    """
    async with session.get(URL_CONTENT + path_dir) as response:
        try:
            check_response_status(response)
            # print("Read directory: " + path_dir)
            return await response.json()
        except ConnectionError:
            print(f'It is not possible to load a list of files '
                  f'from the directory gitea "{path_dir}".')
            return []


def get_hash_file(file_path: str):
    """
    Возвращает ХЭШ-сумму содержимого файла

    :param file_path: полное наименование файла
    :return:
    """
    with open(file_path, "rb") as file:
        _bytes = file.read()
        return sha256(_bytes).hexdigest()


def print_hash_files(_file_list):
    """ Отображает хэш-суммы файлов """
    for file in _file_list:
        print(f"{file}: {get_hash_file(file)}")


async def main():
    """
    Открывает сессию для выполнения HTTP-запрсов для загрузки файлов во рвеменный каталог,
    и далее расчитывает и отображает HASH сумму каждого файла.
     """
    with TemporaryDirectory() as temp_dir:
        async with ClientSession() as session:
            tasks = []
            await create_tasks_download_files(
                session, tasks, await get_list_files(session), temp_dir)
            await asyncio.wait(tasks)
        print_hash_files(file_list)


if __name__ == '__main__':
    # asyncio.run(main(), debug=True)
    asyncio.get_event_loop().run_until_complete(main())
