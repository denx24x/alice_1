from flask import Flask, request
import json
import os
import pymorphy2

app = Flask(__name__)
sessionStorage = {}
morph = pymorphy2.MorphAnalyzer()


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return
    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ] or any([morph.parse(i)[0].normal_form in ['покупать'] for i in req['request']['original_utterance'].lower().split()]):
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })
    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', threaded=True)
