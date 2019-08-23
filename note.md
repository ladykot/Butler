# Учимся использовать API сервиса Yandex SpeechKit




После прочтения статьи вы сможете:
* разобраться, что же такое API на простых примерах (mac os)
* познакомиться с сервисом распознавания и синтеза речи от Yandex
* сделаете своего первого голосового ассистента-дворецкого

[1. Подготовимся. Настройка профиля CLI](#d) 

   [– Активация аккаунта на облаке](#m)
   
   [– В облака – через командную строку](#n)

[2. Знакомство с API Yandex SpeechKit](#l)

   [– Синтез текста через cURL](#o)
   
   [– Распознавание текста с помощью requests](#p)
   
[3. Если вам позвонили из Yandex. Эти загадочные токены  ](#r)
    

## 1. Подготовимся. Настройка профиля CLI <a name="d"></a>

### Активация аккаунта на облаке <a name="m"></a>

Для использования сервиса YSK у вас должна быть почта на Y. 

Заходим на [cloud.yandex](https://cloud.yandex.ru/) и подключаемся. Вуаля – теперь мы на облаке и можно активировать пробный период пользования сервисом. 
Заполните поля, привяжите карту и вам будет предложен грант на 60 дней. 

Ваш платежный аккаунт должен быть в статусе ACTIVE. 

### В облака – через командную строку <a name="n"></a>

Для понимания, как работает распознавание и синтез, мы потренируемся 
в командной строке. Например, в iTerm. 

Для отправки запросов на API через командную строку установим утилиту cURL. Перед установкой проверьте, возможно, она у вас уже есть ($ curl --version):

    $ brew install curl
    
Теперь настроим Интерфейс Яндекс.Облака для командной строки (CLI). 
Запустим скрипт:

    $ curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash

Перезапустите командную оболочку. В переменную окружения PATH добавится путь к исполняемому файлу – *install.sh*.

**Теперь нам нужно, чтобы в CLI заработало автодополнение команд в bash:**

Если у вас еще нет менеджера пакетов Homebrew, [установите его](https://brew.sh/). Он вам не раз пригодится, обещаю. 
	
Затем ставим пакет *bash-completion*: 

    $ brew install bash-completion     
	
   и посмотрим, что изменилось  в файлике *~/.bash_profile (~/.bash_profile используется для пользовательских настроек 
	(в частности  – для определения переменных окружения))*:

    $ open ~/.bash_profile
	
Видим, что в конце *bash_profile* добавились новые строчки:

    .
    .
    # The next line updates PATH for Yandex Cloud CLI.
	...
	
    # The next line enables shell command completion for yc.
	...

Выше новых строк вставьте эту:

    if [ -f $(brew --prefix)/etc/bash_completion ]; then
    . $(brew --prefix)/etc/bash_completion
    fi


Порядок! 
А теперь пристегнитесь, приступаем к инициализации и получаем наш первый “ключик”.  
[В пункте 1](https://cloud.yandex.ru/docs/cli/quickstart#initialize) вам предложат перейти по ссылке, и в отдельном окне появится *aouth_token*

Набираем команду:

    $ yc init

ловите приветственный мессадж:

	Welcome! This command will take you through the configuration process.
    Pick desired action:
 	[1] Re-initialize this profile 'default' with new settings
 	[2] Create a new profile
    Please enter your numeric choice:
	
    # профиль пока нас устраивает, поэтому выбирайте 1

Вам предложат выбрать облако (скорее всего у вас оно единственное):

    You have one cloud available: 'cloud' (id = <цифрыибуквывашейпапочки>). 
    It is going to be used by default.
    Please choose folder to use:
    [1] default (id = <цифрыибуквывашейпапочки>)
    [2] Create a new folder
    
    # новая папка нам пока ни к чему :)

Далее по желанию выберете Compute zone. Пока полоьзователь один – этим можно пренебречь.

Посмотрим, как выглядят настройки профиля CLI:

    $ yc config list

    token: AgAAAAAAHzS2AATuwTpDlcC9LExto-7iIHEWH9o
    cloud-id: b1gthramkv9de6i2ll5n
    folder-id: b1gdt133kktmm89lr51l
    compute-default-zone: ru-central1-b
    

Штош, мы в шаге от старта! Осталось добыть второй ключ (в настройках профиля он не будет отображаться):

    $ yc iam create-token
    
    # приготовьтесь, будет много символов

Полетели!

## 2. Знакомство с API Yandex SpeechKit <a name="l"></a>
	
Представьте простую, максимально идеальную ситуацию без подводных камней типа  “а если..”. Вы организуете закрытую вечеринку и хотите общаться с гостями, ни на что не отвлекаясь. Тем более на тех, кого вы не ждали.

Давайте попробуем создать виртуального дворецкого, который будет встречать гостей и открывать дверь только приглашенным.

### Синтез текста через cURL <a name="o"></a>

С помощью встроенной в bash команды export запишем данные в переменные:
    
    $ export FOLDER_ID=b1gvmob95yysaplct532
    $ export IAM_TOKEN=CggaATEVAgA… 

Теперь их можно передать в POST-запрос с помощью cURL:

    $ curl -X POST \
        -H "Authorization: Bearer ${IAM_TOKEN}" \
        -o speech.raw \
        --data-urlencode "text=Привет, чувак! Назови-ка мне свои имя и фамилию?" \
        -d "lang=ru-RU&folderId=${FOLDER_ID}&format=lpcm&sampleRateHertz=48000\
    &emotion=good&voice=ermil" \
        https://tts.api.cloud.yandex.net/speech/v1/tts:synthesizec
	
	# в командной оболочке делайте все в одну строку, без “\”
   
Рассмотрим параметры запроса:

**speech.raw** – файл формата LPSM (несжатый звук). Это и есть озвученный текст в бинарном виде, который будет сохранен в текущую папку

**lang=ru-RU** – язык текста

**emotion=good** – эмоциональный окрас голоса. Пусть будет дружелюбным

**voice=ermil** – текст будет озвучен мужским голосом Ermil. По умолчанию говорит Оксана

**https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize** – url, на который отправляется post-запрос на синтез речи дворецкого

Бинарный файл послушать не получится, тогда установим утилиту *SoX* и сделаем конвертацию в wav:

    $ brew install sox
    $ sox -r 48000 -b 16 -e signed-integer -c 1 speech.raw speech.wav

**speech.wav** – приветствие готово и сохранено в текущую папку.

Для проигрывания *wav* внутри кода python, можно взять, например, библиотеку *simpleaudio*. Она простая и не создает других потоков:

    import simpleaudio as sa

    def wave_play(trek):
        wave_obj = sa.WaveObject.from_wave_file(trek)
        play_obj = wave_obj.play()
        play_obj.wait_done()

	wave_play(speech.wav)

Итак, наш первый гость стоит перед входом на долгожданную party. Пытается открыть дверь, и вдруг слышит голос откуда-то сверху:

*"Привет, чувак! Назови-ка мне свои имя и фамилию?"*  (или ваш вариант)

Отлично! Вы научили дворецкого приветствовать гостей, используя командную строку и cURL.
А пока гость вспоминает ответ, научимся работать с API на языке python. 

### Распознавание текста с помощью requests <a name="p"></a>

Мы могли бы снова воспользоваться cURL для отправки ответа гостя на распознавание.
Но мы пойдем дальше и напишем небольшую программу.

Создайте готовый аудио-файл с ответом гостя. Сделать это можно через встроенный микрофон на вашем ноутбуке разными инструментами. 
Для macos подойдет Quick Time Player. Сконвертируйте аудио в формат ogg: name_guest.ogg.  Можно онлайн, например, [тут](https://online-audio-converter.com/ru/)

**Итак, пишем код на python:**

Для отправки запросов в python воспользуемся стандартной библиотекой requests:

    $ pip install requests

Импортируем в код:

    import json 
    import requests
    
Зададим параметры, которые мы получили в командной строке:

    URL = https://stt.api.cloud.yandex.net/speech/v1/stt:recognize 
    IAM_TOKEN = "CggaATEVAgA..."
    ID_FOLDER = "b1gdt133kktmm89lr51l"
     
Аудио необходимо передавать в запрос в бинарном виде:

    with open("name_guest.ogg", "rb") as f: 
        name_guest = f.read()
        
Давайте обернем весь процесс распознавания в функцию  *recognize*:

    def recognize(name_guest, IAM_TOKEN, ID_FOLDER):
        """ Функция распознавания русской речи
    
        :param IAM_TOKEN: (str)
        :param outh_guest: ответ гостя (bytes)
        :param ID_FOLDER: (str)
        :return text: (str)
        
        """
        # в поле заголовка передаем IAM_TOKEN:
        headers = {'Authorization': f'Bearer {IAM_TOKEN}'}
        
        # остальные параметры:
        params = {
            'lang': 'ru-RU',
            'folderId': ID_FOLDER,
            'sampleRateHertz': 48000,
        }
    
        response = requests.post(URL_REC, params=params, headers=headers, data=data_sound)
        
        # бинарные ответ доступен через response.content, декодируем его:
        decode_resp = response.content.decode('UTF-8')
        
        # и загрузим в json, чтобы получить текст из аудио:
          
        text = json.loads(decode_resp)
        
        return text

Итак, чтобы дворецкий смог проверить гостя по списку, вызовем функцию и распознаем ответ:

    name = recognize(name_guest, IAM_TOKEN, ID_FOLDER)
    
    print(f"Гость утвержадет, что его зовут: {name}")
    
Теперь очередь за дворецким. В нашем случае, он вежлив ко всем. 
И прежде чем открыть или не открыть гостю дверь, он обратится лично.
Например, так:
	
*“Мы вам очень рады, <имя_и фамилия_гостя>, но вас нет в списке, сорян”*

Для последующего синтеза вы можете снова воспользоваться CURL или так же написать функцию на python.
Принцип работы с API для синтеза и распознавания речи примерно одинаков.

## Если вам позвонили из Yandex. Эти загадочные токены <a name="r"></a>

Возможно, распознавать и синтезировать речь вам так понравится, что однажды вам позвонит милая девушка
из Yandex и поинтересуется, все ли вам понятно в работе сервиса. 

Продолжайте изучать [документацию](https://cloud.yandex.ru/docs/speechkit/), и тогда вы
узнаете, например, что iam_token живет не более 12 часов.

Чтобы быть вежливым (как наш дворецкий) и не перегружать сервера на Yandex, мы не можем генерировать
iam_token чаще. Поэтому заведите себе блокнотик и карандашик для записи даты генерации. Шутка.

Ведь у нас есть python. Создадим функцию для корректной генерации. Снова используем requests:
    
    import json
    import requests
    
    oauth_token = "AgAAAAAAHzS2AATuwTpDlcC9LExto-7iIHEWH9o"
    
    def create_token(oauth_token):
        params = {'yandexPassportOauthToken': oauth_token}
        response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens', params=params)                                                   
        decode_response = response.content.decode('UTF-8')
        text = json.loads(decode_response) 
        iam_token = text.get('iamToken')
        expires_iam_token = text.get('expiresAt')
        
        return iam_token, xpires_iam_token
        
Вызовем функцию и положим результат в переменную:

    result = create_token(oauth_token)
    print("Токен успешно сгенерирован и действует до {}".format(result[1]))

Штош, карандишик и блокнотик не пострадали, 
а у вас появилась полезная переменная *xpires_iam_token*. 








