import os
from hashlib import sha256
from time import sleep
from datetime import datetime
from typing import Dict, Optional

try:
    from dotenv import load_dotenv
    from loguru import logger
    from yandex_disk import YandexDisk
except Exception as e:
    print('Ошибка импорта: ', e)
    print(
        'Для установки необходимых модулей выполните команду: "pip install -r requirements.txt" из папки с программой')
    sleep(15)
    exit(1)


class CloudSync:
    """
    A class that provides a program for synchronizing a local folder with Yandex Disk.
    """

    def __init__(self) -> None:
        self.load_env()
        self.activate_logger()
        self.cloud_module = YandexDisk(token=os.getenv('API_TOKEN'), cloud_path=os.getenv('CLOUD_FOLDER'))
        self.main_loop()

    def load_env(self) -> None:
        """
        The method that initializes working with .env
        """
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        else:
            logger.error('Отсутствует файл конфигурации .env, проверьте его наличие и настройки.')
            exit()

    def activate_logger(self) -> None:
        """
        The method that activates logging
        """
        log_file_path = os.path.join(os.getenv('LOG_PATH'), datetime.now().strftime('%d.%m.%Y') + '.log')
        logger.add(log_file_path,
                   format="CloudSync | {time:DD-MM-YYYY  HH:mm:ss} | {level} | {message}",
                   level='DEBUG')
        logger.info("Программа синхронизации файлов начинает работу с директорией {}".format(os.getenv('LOCAL_FOLDER')))

    def main_loop(self) -> None:
        """
        The method that performs the main synchronization loop.
        """
        sleep_time = float(os.getenv('SYNC_PERIOD'))
        while 1:
            local_files = self.get_local_files()
            cloud_files = self.get_cloud_files()
            self.compare_folders(local_files, cloud_files)
            sleep(sleep_time)

    def get_local_files(self) -> Dict[str, str]:
        """
        The method that creates a dictionary of local files and their hash sums
        :return: dictionary of local files and their hash sums
        :rtype: Dict[str, str]
        """
        try:
            local_folder = os.getenv('LOCAL_FOLDER')
            local_file_names = os.listdir(local_folder)
            local_files = dict()
            for file_name in local_file_names:
                file_path = os.path.join(local_folder, file_name)
                hash_sum = self.get_file_hash(file_path)
                if hash_sum is not None:
                    local_files[file_name] = hash_sum
            return local_files
        except FileNotFoundError:
            logger.error(
                'Не удалось открыть директорию {}, проверьте файл конфигурации'.format(os.getenv('LOCAL_FOLDER')))
            exit()

    def get_cloud_files(self) -> Optional[Dict[str, str]]:
        """
        The method that creates requests a dictionary of cloud files and their hash sums
        :return: dictionary of cloud files and their hash sums
        :rtype: Dict[str, str]
        """
        request_to_cloud = self.cloud_module.get_info()
        if request_to_cloud is not None:
            cloud_files = dict()
            for item in request_to_cloud['_embedded']['items']:
                cloud_files[item['name']] = item['sha256']
            return cloud_files
        else:
            return None

    def compare_folders(self, local_files: Dict[str, str], cloud_files: Dict[str, str]) -> None:
        """
        The method that compares local and cloud files and accordingly calls load, reload,
        or delete methods from cloud module

        :param local_files: dictionary of local files
        :type local_files: Dict[str, str]
        :param cloud_files: dictionary of cloud files
        :type cloud_files: Dict[str, str]
        """

        load_list = list()
        reload_list = list()
        delete_list = list()

        for name, hash_sum in local_files.items():
            if name in cloud_files:
                if cloud_files[name] != hash_sum:
                    reload_list.append(os.path.join(os.getenv('LOCAL_FOLDER'), name))
                del cloud_files[name]
            else:
                load_list.append(os.path.join(os.getenv('LOCAL_FOLDER'), name))

        if len(cloud_files) > 0:
            delete_list = [key for key, value in cloud_files.items()]

        if delete_list:
            self.cloud_module.delete(delete_list)
        if load_list:
            self.cloud_module.load(load_list)
        if reload_list:
            self.cloud_module.reload(reload_list)

    def get_file_hash(self, file_path: str) -> Optional[str]:
        """
        The method that calculates the sha-256 hash of a file

        :param file_path: path to file
        :type file_path: str
        :return: sha-256 hash
        :rtype: str
        """
        sha256_hash = sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except PermissionError:
            logger.error('Не удалось открыть файл {}. Ошибка разрешения доступа.'.format(file_path))
            return None
        except OSError:
            logger.error('Не удалось открыть файл {}.'.format(file_path))


if __name__ == '__main__':
    cloud_sync = CloudSync()
