import aiofiles

from http import HTTPStatus

import os


class FakeClientResponse:
    """ Класс Подделього ответа сессии """

    def __init__(self, filename: str, status: int):
        self._filename = filename
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def content(self):
        return FileContent(self._filename)


class FileContent:
    def __init__(self, filename):
        self._filename = filename

    async def read(self):
        # file_name = "download_gitea_repository/tests/conftest.py"
        async with aiofiles.open(self._filename, 'rb') as file:
            return await file.read()


class FakeClientSession:
    def get(self, url):
        filename = os.path.basename(url)
        full_filename = os.path.join(os.getcwd(), f"download_gitea_repository/tests/{filename}" )
        if os.path.exists(full_filename):
            return FakeClientResponse(full_filename, HTTPStatus.OK)
        else:
            return FakeClientResponse("", HTTPStatus.BAD_REQUEST)
