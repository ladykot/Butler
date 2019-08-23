import json
import logging
import os
import requests
import simpleaudio as sa

from config import env_set
from pydub import AudioSegment


URL = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
URL_REC = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
URL_SYN = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

PATH = 'iam.txt'

guest_list = ["Васечкин", "Билан"]

#  запишем в логи информацию о токенах:
log_format = '%(asctime)s - %(message)s'
logging.basicConfig(filename='sample.log',
                    format=log_format,
                    level=logging.INFO)


def sound(trek):
    """ функция проигрывания аудио

    :param: trek (wav)

    """
    wave_obj = sa.WaveObject.from_wave_file(trek)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def write_token(iam_new):
    """ Функция записывает новый iam токен в файл

    :param iam_new: (str)
    """
    with open(PATH, 'w') as f:
        f.write(iam_new)


def create_new_token():
    """ Функция генерирует новый токен обменом oauth_token на iam-токен
    и записывет в iam.txt

    :return: iam_new (str)
    """
    logging.info('Время iam_token истекло. Отправка запроса ...')

    params = {'yandexPassportOauthToken': oauth_token}  # указали oauth_token в параметрах запроса
    response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens',
                             params=params)
    decode_response = response.content.decode('UTF-8')  # декодируем бинарник
    text = json.loads(decode_response)  # загружаем в json
    iam_new = text.get('iamToken')  # iam_token << json по ключу iamToken
    expires_iam_token = text.get('expiresAt')

    write_token(iam_new)
    logging.info("Новый iam-токен успешно сгенерирован. "
                 f"Срок жизни: до {expires_iam_token}")
    return iam_new


def get_token():
    """ Функция проверяет работоспособность iam-токен.

    Если при попытке аторизации c iam-токен приходит ошибка,
    то генерируется и записывается в файл новый iam-токен вызовом функции create_token().

    """
    if os.path.exists(PATH):  # если уже получали токен и файл существует
        with open('iam.txt', 'r') as f:
            iam = f.read()
            headers = {'Authorization': f'Bearer {iam}'}
            data = {'text': "проверка",
                    'lang': 'ru-RU',
                    'folderId': id_folder}
            resp = requests.post(URL_SYN, headers=headers, data=data)
            if resp.status_code == 200:
                logging.info('iam-токен еще действует')
                return iam
            else:
                return create_new_token()
    else:  # если файла c iam-токеном еще не существует
        iam_new = create_new_token()
        write_token(iam_new)
        return iam_new


def butler(text):
    """ Функция синтеза речи дворецкого из текста

    :param text: (str)
    :return: sync.wav
    """

    headers = {
        'Authorization': f'Bearer {iam_token}',
    }

    data = {
        'text': text,
        'lang': 'ru-RU',
        'folderId': id_folder,
        'speed': 1.0,
        'emotion': 'good',
        'voice': 'ermil'
    }

    resp = requests.post(URL_SYN, headers=headers, data=data, stream=True)  # делаем запрос на синтез текста
    if resp.status_code != 200:
        raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
    with open('butler_hello.ogg', 'wb') as f:
        f.write(resp.content)  # запись в .ogg
    AudioSegment.from_file('butler_hello.ogg').export('butler_hello.wav', format="wav")  # конвертация в wav
    sound('butler_hello.wav')


def recognize_guest(audio_data):
    """ Функция распознавания речи гостя

    :param audio_data: ответ гостя (ogg)
    :return text: (str)

    """

    with open(audio_data, "rb") as f:
        data = f.read()
    headers = {'Authorization': f'Bearer {iam_token}'}
    params = {
        'lang': 'ru-RU',
        'folderId': id_folder,
        'sampleRateHertz': 48000,
    }
    response = requests.post(URL_REC, params=params, headers=headers, data=data)  # отправка post-запроса
    decode_resp = response.content.decode('UTF-8')  # декодируем
    text = json.loads(decode_resp)  # загружаем в json
    if text.get('error_code') is None:
        text = text.get('result')  # забираем текст из json по ключу result
        print(f'Гость ответил ... {text}')
    else:
        print(text.get('error_code'))
        logging.debug('Дворецкий недоступен. Попробуйте позже')
        return False
    return text


if __name__ == '__main__':
    if env_set():  # задаем переменные окружения
        oauth_token = os.environ['oauth_token']  # и кладем их в рабочие переменные
        id_folder = os.environ['id_folder']
    iam_token = get_token()  # задаем iam-токен (берем текущий или генерируем новый)

    # стук в дверь:
    sound('bell_door.wav')
    # пусть дворецкий спросит гостя, как его зовут, например, так:
    butler("Привет,чувак! Назови мне только свою фамилию!")
    # распознаем ответ гостя:
    guest = recognize_guest("audio_guest.ogg")

    if guest in guest_list:
        butler(f"Рад тебя видеть, {guest}! заходь!")
        # дверь открывается:
        sound('open_door.wav')
    else:
        butler(f"Рад тебя видеть, {guest}! но тебя нет в списке, сорян!")






