import os

import requests


class YandexCloud:
    def load(self, path, overwrite=False):

        if path is not list:
            path = list(path)

        for item in path:
            url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            headers = {
                "Authorization": f"OAuth {os.getenv('API_TOKEN')}",
            }
            cloud_path = os.getenv('CLOUD_FOLDER') + '/' + os.path.basename(item)
            params = {
                "path": cloud_path,
                "overwrite": overwrite,
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                cloud_file_href = data['href']
                try:
                    files = {"file": open(item, "rb")}
                    response = requests.put(cloud_file_href, files=files)
                    # TODO log info
                except Exception as ex:
                    # TODO log error
                    print(ex)
            else:
                print("Ошибка при выполнении запроса:", response.status_code)

    def reload(self, path):
        self.load(path=path, overwrite=True)

    def delete(self, filename):
        pass

    def get_info(self, token, path):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {
            "Authorization": f"OAuth {token}",
        }
        params = {
            "path": path,
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            # TODO log info
            return response.json()
        else:
            pass
        # TODO log error
