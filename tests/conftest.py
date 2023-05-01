import os
from http import HTTPStatus
from typing import Final

import pytest

from .mocks import FakeClientSession, FakeClientResponse
from ..working_file import GITEA_DOMAIN

FAKE_URL: Final = "https://fake.domain.local/path/"


@pytest.fixture()
def list_hash():
    """
    Возвращает список расчитанных HASH-сумм файлов
    создаваемых фикстурой list_files
    """
    return ['75e0d458fc2da40b5b8b8b614d0192e9da7fffc2d6042f33300fdb0e8a83dfb4',
            'd1988cd3019824f075f61677e1a6f54b16035868488e4051757dde53adeef80f',
            '9597d898814f165b7ed6118722c24271fec8c1254d46e437ad6ab24050763e2d',
            'b910ce7ef3d90e013867bae074fcccaed29ee9262a006ef5af04c06d9b6bc1eb',
            'cabb866ab5c902410cac8f414d84700d943bfb0ee900c8f72fe150cc7e70ad65',
            '5c4d07d51cc27f5f1eef4bd79e2e2db88beec0df0796ee134b31178538d0ccb3']


@pytest.fixture()
def list_files(tmp_path):
    """
    Формирует список файлов с определённым содержимым
    и возвращает список их полных наименований
    """
    list_files = []
    for i in range(6):
        filename = os.path.join(tmp_path, f"file_{i}.dat")
        with open(filename, "w") as f:
            f.write(f"content {i}")
        list_files.append(filename)
    return list_files


@pytest.fixture()
def temp_files(list_files: list, list_hash: list):
    """
    Создаёт временные файлы для проверки расчета HASH-суммы,
    и объединяет список с уже рассчитанными для них HASH суммами
    """
    return list(zip(list_files, list_hash))


@pytest.fixture()
def patched_constant_url_content(monkeypatch):
    """ Патчит константу URL_CONTENT """
    repository = "radium/monitoring"
    patched = f"{GITEA_DOMAIN}/api/v1/repos/{repository}/contents/"
    monkeypatch.setattr("download_gitea_repository.working_file.URL_CONTENT", patched)
    return patched


@pytest.fixture()
def patched_constant_url_download(monkeypatch):
    """ Патчит константу FAKE_URL """
    monkeypatch.setattr("download_gitea_repository.working_file.URL_DOWNLOAD", FAKE_URL)
    return FAKE_URL


def list_files_params1():
    return ("", [
        {'name': "obsdsnmp", 'type': 'dir'},
        {'name': "tests", 'type': 'dir'},
        {'name': ".gitignore", 'type': 'file'},
        {'name': "LICENSE", 'type': 'file'},
        {'name': "README.md", 'type': 'file'},
        {'name': "poetry.lock", 'type': 'file'},
        {'name': "pyproject.toml", 'type': 'file'},
        {'name': "pytest.ini", 'type': 'file'},
        {'name': "setup.cfg", 'type': 'file'}
    ])


def list_files_params2():
    return ("obsdsnmp", [
        {'name': "__init__.py", 'type': 'file'},
        {'name': "__main__.py", 'type': 'file'},
        {'name': "models.py", 'type': 'file'}
    ])


def list_files_params_idfn(val):
    return f'dir: "{val[0]}"'


@pytest.fixture(scope="function", params=[
    list_files_params1(), list_files_params2()
], ids=list_files_params_idfn)
def list_files_params(request):
    """ Параметры для тестирования возврата файлов из gitea репозитория """
    return request.param


@pytest.fixture()
async def fake_session():
    """ Создаёт поддельную сессию """
    return FakeClientSession()


@pytest.fixture()
async def fake_response(tmp_path):
    """ Создаёт поддельный ответ """
    filename = "download_gitea_repository/tests/conftest.py"
    return FakeClientResponse(filename, HTTPStatus.OK)