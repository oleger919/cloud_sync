import requests


class YandexCloud:
    def load(self, local_path, cloud_path, token):

        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {
            "Authorization": f"OAuth {token}",
        }
        params = {
            "path": cloud_path,
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            cloud_file_href = data['href']
            try:
                files = {"file": open(local_path, "rb")}
                response = requests.put(cloud_file_href, files=files)
                # TODO log info
            except Exception as ex:
                # TODO log error
                print(ex)


        else:
            print("Ошибка при выполнении запроса:", response.status_code)

    def reload(self, path):
        pass

    def delete(self, filename):
        pass

    def get_info(self, path):
        pass
