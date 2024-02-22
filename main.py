import hashlib
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
from yandex_cloud import YandexCloud


class CloudSync:
    def __init__(self):
        self.load_env()
        self.activate_logger()
        self.yandex_cloud = YandexCloud(token=os.getenv('API_TOKEN'), cloud_path=os.getenv('CLOUD_FOLDER'))
        self.main_loop()

    def load_env(self):
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

    def activate_logger(self):
        log_file_path = os.path.join(os.getenv('LOG_PATH'), datetime.now().strftime('%d.%m.%Y') + '.log')
        logger.add(log_file_path,
                   format="CloudSync | {time:DD-MM-YYYY  HH:mm:ss} | {level} | {message}",
                   level='DEBUG')
        logger.info("Программа синхронизации файлов начинает работу с директорией {}".format(os.getenv('LOCAL_FOLDER')))

    def main_loop(self):
        sleep_time = float(os.getenv('SYNC_PERIOD'))
        while 1:
            local_files = self.get_local_files()
            cloud_files = self.get_cloud_files()
            self.compare_folders(local_files, cloud_files)
            time.sleep(sleep_time)

    def get_local_files(self):
        # создать словарь локальных файлов
        try:
            local_folder = os.getenv('LOCAL_FOLDER')
            local_file_names = os.listdir(local_folder)
            local_files = dict()
            for file_name in local_file_names:
                file_path = os.path.join(local_folder, file_name)
                local_files[file_name] = self.get_file_hash(file_path)
            return local_files
        except FileNotFoundError:
            logger.error(
                'Не удалось открыть директорию {}, проверьте файл конфигурации'.format(os.getenv('LOCAL_FOLDER')))
            return

    def get_cloud_files(self):
        # получить словарь облачных файлов
        request_to_cloud = self.yandex_cloud.get_info()
        if request_to_cloud is not None:
            cloud_files = dict()
            for item in request_to_cloud['_embedded']['items']:
                cloud_files[item['name']] = item['sha256']
            return cloud_files
        else:
            return

    def compare_folders(self, local_files, cloud_files):
        # сравнить словари в цикле и получить списки файлов для загрузки, перезалива и удаления
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

        # выполнить действия
        if delete_list:
            self.yandex_cloud.delete(delete_list)
        if load_list:
            self.yandex_cloud.load(load_list)
        if reload_list:
            self.yandex_cloud.reload(reload_list)

    def get_file_hash(self, file_path):
        """Вычисляет хэш SHA-256 файла."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()


if __name__ == '__main__':
    cloud_sync = CloudSync()
