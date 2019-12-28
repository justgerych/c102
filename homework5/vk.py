import requests
import time
import datetime

import pandas as pd
import textwrap
from pandas.io.json import json_normalize
from string import Template
from tqdm import tqdm
from igraph import Graph, plot
import numpy as np

domain = "https://api.vk.com/method"
access_token = "f068c7c36ae15f73041bbb02a49a077456c40891d941bf110b4b372ea591b9e9d64aeda8165de37f2d633"
v = '5.103'


def get_friends(user_id, fields=""):
    """ Returns a list of user IDs or detailed information about a user's friends """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert isinstance(fields, str), "fields must be string"
    assert user_id > 0, "user_id must be positive integer"
    query = f"{domain}/friends.get?user_id={user_id}&fields={fields}&access_token={access_token}&v={v}"
    response = requests.get(query)
    return response.json()


def get(url, params={}, timeout=5, max_retries=5, backoff_factor=0.3):
    """ Выполнить GET-запрос

    :param url: адрес, на который необходимо выполнить запрос
    :param params: параметры запроса
    :param timeout: максимальное время ожидания ответа от сервера
    :param max_retries: максимальное число повторных запросов
    :param backoff_factor: коэффициент экспоненциального нарастания задержки
    """
    try:
        for _ in range(max_retries):
            resp = requests.get(url, params, timeout=(3.05, timeout))
            if resp.status_code == 500:
                raise requests.exceptions.HTTPError("HTTPError: 500 Server Error: INTERNAL SERVER ERROR ...")
            else:
                print(resp.status_code)
            time.sleep(timeout * backoff_factor)
    except requests.exceptions.ReadTimeout as e:
        print(e.args)
    except requests.exceptions.HTTPError as e:
        print(e.args)
    except requests.exceptions.ConnectionError as e:
        print(e.args)


def age_predict(user_id):
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"

    friends = get_friends(user_id, fields="bdate")

    pred_age = 0
    friends_with_date = 0

    date_format = "%d.%m.%Y"

    for friend in friends["response"]["items"]:
        try:
            bdate = friend["bdate"]
            bdate = datetime.datetime.strptime(bdate, date_format)
            pred_age += (datetime.date.today() - bdate.date()) // datetime.timedelta(days=365)
            friends_with_date += 1
        except KeyError:
            pass
        except ValueError:
            pass
    pred_age = pred_age // friends_with_date
    print(pred_age)


########HERE###############
def get_network(users_ids, as_edgelist=True):
    """ Building a friend graph for an arbitrary list of users """
    edges = []
    amount = 0
    for ind1 in range(len(users_ids)):
        for ind2 in range(len(users_ids)):
            try:
                if users_ids[ind2] in get_friends(users_ids[ind1])['response']['items']:
                    edges += [(ind1, ind2)]
                    amount += 1
            except KeyError:
                pass

    g = Graph(vertex_attrs={"label": users_ids},
              edges=edges, directed=False)

    plot_graph(g, amount)


def plot_graph(graph, vertices):
    N = vertices
    visual_style = {}
    visual_style["layout"] = graph.layout_fruchterman_reingold(
        maxiter=1000,
        area=N ** 3,
        repulserad=N ** 3)

    plot(graph, **visual_style)


def get_wall(
        owner_id: str = '',
        domain: str = '',
        offset: int = 0,
        count: int = 10,
        filter: str = 'owner',
        extended: int = 0,
        fields: str = '',
        v: str = '5.103'
) -> pd.DataFrame:
     """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param v: Версия API.
    """
    code = ("return API.wall.get({" +
            f"'owner_id': '{owner_id}'," +
            f"'domain': '{domain}'," +
            f"'offset': {offset}," +
            f"'count': {count}," +
            f"'filter': '{filter}'," +
            f"'extended': {extended}," +
            f"'fields': '{fields}'," +
            f"'v': '{v}'," +
            "});")

    response = requests.post(
        url="https://api.vk.com/method/execute",
        data={
            "code": code,
            "access_token": access_token,
            "v": v
        }
    )

    return response.json()['response']['items']


def prepare(texts):
    pass

def median(list_of_numbers):
    list_of_numbers = sorted(list_of_numbers)
    if len(list_of_numbers) != 0:
        index = len(list_of_numbers) // 2
        print(list_of_numbers[index])
        return list_of_numbers[index]

median([11,9,3,5,5])


# age_predict(238472934)
#get_network([238472934, 313489913, 125483792, 81552651])
# print(get_friends(238472934))
# print(get_wall(domain="itmoru"))
# a = get_wall(domain="itmoru")
# texts = []

# print(a[0]["text"])
# print(a[1]["text"])

# prepare(texts)
