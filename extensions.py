import requests
import json
from config import AKEY, currencies

class APIException(Exception):
    pass

class Forex:
    @staticmethod
    def get_price(cur_to, cur_from, amount):
        if cur_from == cur_to:
            raise APIException("Введены одинаковые валюты.")
        try:
            list(currencies.keys()).index(cur_from)
        except ValueError:
            raise APIException("Исходной валюты нет в списке.")
        try:
            list(currencies.keys()).index(cur_to)
        except ValueError:
            raise APIException("Валюты конвертации нет в списке.")
        try:
            amount = float(amount)
        except ValueError:
            raise APIException("Введи количество валюты для конвертации в числовом формате.")

        r = requests.get(f"https://free.currconv.com/api/v7/convert?q={currencies[cur_from]}_{currencies[cur_to]}&compact=ultra&apiKey={AKEY}")
        conv_rate = json.loads(r.content).values()
        conv_rate_list = list(json.loads(r.content).values())
        result = float(conv_rate_list[0]) * float(amount)
        return result