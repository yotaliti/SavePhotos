import json
import requests
from tqdm import tqdm


class APIVKclient:
    API_BASE_URL = 'https://api.vk.com/method'
    url_yadisk = 'https://cloud-api.yandex.net'

    def __init__(self, token_vk, owner_id, token_ya):
        self.token_vk = token_vk
        self.token_ya = token_ya
        self.owner_id = owner_id

    def get_common_params(self):
        return {
            'access_token': self.token_vk,
            'v': '5.199',
            'album_id': 'profile',
            'extended': 1
        }

    def get_photo_info(self):
        params = self.get_common_params()
        params.update({'owner_id': self.owner_id})
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        photo_info = response.json()['response']['items'][:5]
        return photo_info

    def create_folder_url(self):
        url_create_folder = f'{self.url_yadisk}/v1/disk/resources'
        params = {
            'path': 'Photos'
        }
        headers = {
            'Authorization': self.token_ya
        }
        requests.put(url_create_folder, params=params, headers=headers)
        url_get_upload = f'{self.url_yadisk}/v1/disk/resources/upload'
        return url_get_upload

    def save_photos(self):
        result = []
        for photo in tqdm(self.get_photo_info(), desc="Процесс выполнения"):
            url_image = photo['sizes'][-1]['url']
            response_photo = requests.get(url_image)
            name_photo = f'{photo['likes']['count']}.jpg'
            size = photo['sizes'][-1]['type']
            response = requests.get(self.create_folder_url(),
                                    headers={'Authorization': self.token_ya},
                                    params={'path': f'Photos/{name_photo}'}
                                    )
            url_for_upload = response.json().get('href', '')

            with open(f'{name_photo}', 'wb') as file:
                file.write(response_photo.content)
            with open(f'{name_photo}', 'rb') as file:
                requests.put(url_for_upload, files={'file': file})
            result.append({"file_name": name_photo, "size": size})
        with open('json_file.json', 'w') as f:
            json.dump(result, f, indent=2)
        return result
