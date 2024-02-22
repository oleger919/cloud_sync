import json
import os
import requests
from loguru import logger
from typing import Union, List


class YandexDisk:
    """
    A class that implements methods for working with the Yandex disk API.

    Args:
        token (str): pass a cloud storage access token
        cloud_path (str): pass the path of the folder in the cloud storage
    """

    def __init__(self, token: str, cloud_path: str) -> None:
        self.__token = token
        self.__cloud_path = cloud_path

    def load(self, path: Union[str, List[str]], overwrite: bool = False) -> None:
        """
        The method that uploads the file to Yandex disk

        :param path: pass the path to the local file
        :type path: str, List[str]
        :param overwrite: indicates whether the file on the disk needs to be overwritten. True - overwriting is required
        :type overwrite: bool
        """
        if not isinstance(path, list):
            path = list(path)

        for item in path:
            url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            headers = {
                "Authorization": f"OAuth {self.__token}",
            }
            cloud_filepath = self.__cloud_path + '/' + os.path.basename(item)
            params = {
                "path": cloud_filepath,
                "overwrite": overwrite,
            }
            try:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    cloud_file_href = data['href']
                    files = {"file": open(item, "rb")}
                    response = requests.put(cloud_file_href, files=files)
                    if response.status_code == 201:
                        logger.info('Файл {} загружен в облако.'.format(item))
                    else:
                        response_content = json.loads(response.content)
                        logger.error('Не удалось загрузить файл {file} в облако. '
                                     'Код ошибки {error}: {message}'.format(file=item, error=response.status_code,
                                                                            message=response_content['message']))
                else:
                    print("Ошибка при выполнении запроса:", response.status_code)
            except requests.exceptions.ConnectionError:
                logger.error('Не удалось загрузить файл {} в облако. Ошибка соединения.'.format(item))

    def reload(self, path: Union[str, List[str]]) -> None:
        """
        The method that overwrites the file on Yandex disk

       :param path: pass the path to the local file
       :type path: str, List[str]
       """
        self.load(path=path, overwrite=True)

    def delete(self, filename: Union[str, List[str]]) -> None:
        """
        The method that deletes files on Yandex disk

        :param filename: pass the names of files needs to be deleted
        :type filename: str, List[str]
        """

        if not isinstance(filename, list):
            filename = list(filename)

        for item in filename:
            url = "https://cloud-api.yandex.net/v1/disk/resources"
            headers = {
                "Authorization": f"OAuth {self.__token}",
            }
            params = {
                "path": '/'.join([self.__cloud_path, item]),
            }
            try:
                response = requests.delete(url, headers=headers, params=params)
                if response.status_code == 204:
                    logger.info('Файл {} удален из облака'.format(item))
                else:
                    response_content = json.loads(response.content)
                    logger.error('Не удалось удалить файл {file} из облака. '
                                 'Код ошибки {error_code}: {message}'.format(file=item, error_code=response.status_code,
                                                                             message=response_content['message']))
            except requests.exceptions.ConnectionError:
                logger.error('Не удалось удалить файл из облака. Ошибка соединения.')

    def get_info(self):
        """
        The method for getting information about files on Yandex disk

        :return: A dictionary with information about a file or folder in JSON format.
        """
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {
            "Authorization": f"OAuth {self.__token}",
        }
        params = {
            "path": self.__cloud_path,
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                response_content = json.loads(response.content)
                logger.error('Не удалось получить информацию из облака. Код ошибки {code}: {message}'.format(
                    code=response.status_code, message=response_content['message']))
        except requests.exceptions.ConnectionError:
            logger.error('Не удалось получить информацию из облака.Ошибка соединения.')
