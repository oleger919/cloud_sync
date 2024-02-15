import os
from dotenv import load_dotenv
from loguru import logger
from yandex_cloud import YandexCloud

class CloudSync:
    def __init__(self):
        self.load_env()
        #logger.add(os.getenv('LOG_PATH'), level='DEBUG')
        self.yandex_cloud = YandexCloud()
        # YandexCloud.load() # TODO сделать первоначальную выгрузку а потом уходить в цикл отслеживания

        local_path = os.path.join(os.getenv("LOCAL_FOLDER"), "test.txt")
        cloud_path = os.getenv("CLOUD_FOLDER") + "/test.txt"
        self.yandex_cloud.load(local_path, cloud_path, token=os.getenv('API_TOKEN'))
        # self.main_loop()

    def load_env(self):
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

    def main_loop(self):
        while 1:
            pass

    def is_local_files_changed(self):
        pass


if __name__ == '__main__':
    cloud_sync = CloudSync()