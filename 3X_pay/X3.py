import datetime
import json

import requests
import uuid
from config_data.config import load_config
serv = load_config().tg_bot.serv


class X3:
    login = serv[0]
    password = serv[1]
    host = f"http://{serv[2]}"
    header = []
    data = {"username": login, "password": password}
    ses = requests.Session()

    def test_connect(self):
        response = self.ses.post(f"{self.host}/login", data=self.data)
        return response

    def list(self):
        resource = self.ses.get(f'{self.host}/panel/api/inbounds/list', json=self.data).json()
        return resource

    def addClient(self, day, user_name, user_id, count):
        epoch = datetime.datetime.utcfromtimestamp(0)
        x_time = int((datetime.datetime.now() - epoch).total_seconds() * 1000.0)
        x_time += 86400000 * day - 10800000
        header = {"Accept": "application/json"}
        data1 = {
            "id": 9,
            "settings":
                "{\"clients\":"
                "[{\"id\":\"" + str(uuid.uuid1()) + "\", \"flow\": \"xtls-rprx-vision\","
                "\"alterId\":90,\"email\":\"" + str(user_id) + "\","
                "\"limitIp\":" + str(count) + ",\"totalGB\":0,"
                "\"expiryTime\":" + str(x_time) + ", \"enable\":true,\"tgId\":\"" + str(user_name) + "\",\"subId\":\"\"}]}"
        }

        resource = self.ses.post(f'{self.host}/panel/api/inbounds/addClient', headers=header, json=data1)
        return resource

    def updateClient(self, day, user_id, count):
        dict_x = self.time_active(user_id)
        for key, val in dict_x.items():
            if key != '0' and val != '0':
                val /= 1000
                val += 10800
                date_x = datetime.datetime.utcfromtimestamp(val)
                date_x += datetime.timedelta(day)
                epoch = datetime.datetime.utcfromtimestamp(0)
                x_time = int((date_x - epoch).total_seconds() * 1000.0)
                x_time += 86400000 * day - 10800000
                header = {"Accept": "application/json"}
                data1 = {
                    "id": 9,
                    "settings":
                        "{\"clients\":"
                        "[{\"id\":\"" + str(key) + "\", \"flow\": \"xtls-rprx-vision\","
                        "\"alterId\":90,\"email\":\"" + str(user_id) + "\","
                        "\"limitIp\":" + str(count) + ",\"totalGB\":0,"
                        "\"expiryTime\":" + str(x_time) + ",\"enable\":true,\"tgId\":\"""\",\"subId\":\"\"}]}"
                }
                resource = self.ses.post(f'{self.host}/panel/api/inbounds/updateClient/{key}', headers=header, json=data1)
                return resource
            else:
                epoch = datetime.datetime.utcfromtimestamp(0)
                x_time = int((datetime.datetime.now() - epoch).total_seconds() * 1000.0)
                x_time += 86400000 * day - 10800000
                header = {"Accept": "application/json"}
                data1 = {
                    "id": 9,
                    "settings":
                        "{\"clients\":"
                        "[{\"id\":\"" + str(key) + "\", \"flow\": \"xtls-rprx-vision\","
                         "\"alterId\":90,\"email\":\"" + str(user_id) + "\","
                         "\"limitIp\":" + str(count) + ",\"totalGB\":0,"
                         "\"expiryTime\":" + str(x_time) + ",\"enable\":true,\"tgId\":\"" + str(user_id) + "\",\"subId\":\"\"}]}"
                }
                resource = self.ses.post(f'{self.host}/panel/api/inbounds/updateClient/{key}', headers=header,
                                         json=data1)
                return resource


    def updateClientOut(self, user_id):
        dict_x = self.time_active(user_id)
        for key, val in dict_x.items():
            if key == '0' and val == '0':
                header = {"Accept": "application/json"}
                data1 = {
                    "id": 9,
                    "settings":
                        "{\"clients\":"
                        "[{\"id\":\"""\", \"flow\": \"xtls-rprx-vision\","
                        "\"alterId\":90,\"email\":\"" + str(user_id) + "\","
                        "\"limitIp\":"",\"totalGB\":0,"
                        "\"expiryTime\":"",\"enable\":false,\"tgId\":\"""\",\"subId\":\"\"}]}"
                }
                resource = self.ses.post(f'{self.host}/panel/api/inbounds/updateClient/{key}', headers=header, json=data1)
                return resource

    def link(self, user_id: str):
        """
        Получение ссылки!
        :param user_id: str
        :return: str
        """
        id = ''
        y = json.loads(self.list()['obj'][0]['settings'])
        for i in y["clients"]:
            if i['email'] == user_id:
                id = i["id"]
        x = json.loads(self.list()['obj'][0]['streamSettings'])
        tcp = x['network']
        reality = x['security']
        if id =='':
            val = '----'
        else:
             val = f"vless://{id}@bazai15.ru:443/?type={tcp}&security={reality}&pbk=TLjoARquHvFwnYZciHwmi773eehexxv7Q3pjt2f-zyM&fp=chrome&sni=google.com&sid=6c80b3&spx=%2F&flow=xtls-rprx-vision#%F0%9F%A5%91Avocado-{user_id}"
          
        return val

    def time_active(self, user_id: str):
        dict_x = {}
        epoch = datetime.datetime.utcfromtimestamp(0)
        x_time = int((datetime.datetime.now() - epoch).total_seconds() * 1000.0)
        y = json.loads(self.list()['obj'][0]['settings'])
        for i in y["clients"]:
            if i['email'] == user_id:
                if i['enable'] and i['expiryTime'] > x_time:
                    dict_x[i['id']] = i['expiryTime']
                    return dict_x
                else:
                    dict_x[i['id']] = '0'
                    return dict_x
        if len(dict_x) == 0:
            dict_x['0'] = '0'
            return dict_x

    def activ(self, user_id: str):
        """
        Проверка активности подписки
        :param user_id: str
        :return: str
        """
        dict_x = {}
        epoch = datetime.datetime.utcfromtimestamp(0)
        x_time = int((datetime.datetime.now() - epoch).total_seconds() * 1000.0)
        y = json.loads(self.list()['obj'][0]['settings'])
        for i in y["clients"]:
            if i['email'] == user_id:
                if i['enable'] and i['expiryTime'] > x_time:
                    print(i)
                    print(i['enable'])
                    dict_x['activ'] = 'Активен'
                    ts = i['expiryTime']
                    ts /= 1000
                    ts += 10800
                    dict_x['time'] = datetime.datetime.utcfromtimestamp(ts).strftime('%d-%m-%Y %H:%M') + ' МСК'
                    dict_x['key'] = i['limitIp']
                    return dict_x
                else:
                    print(i)
                    print(i['enable'])
                    dict_x['activ'] = 'Не Активен'
                    ts = i['expiryTime']
                    ts /= 1000
                    ts += 10800
                    dict_x['time'] = datetime.datetime.utcfromtimestamp(ts).strftime('%d-%m-%Y %H:%M') + ' МСК'
                    dict_x['key'] = i['limitIp']
                    return dict_x
            else:
                dict_x['activ'] = 'Не зарегистрирован'
                dict_x['time'] = '-'
        return dict_x

    def activ_list(self):
        """
        Проверка активности подписки
        :param user_id: str
        :return: str
        """
        dict_x = {}
        y = json.loads(self.list()['obj'][0]['settings'])
        for i in y["clients"]:
            ts = i['expiryTime']
            ts /= 1000
            ts += 10800
            x = datetime.datetime.now()
            y = datetime.datetime.utcfromtimestamp(ts)
            z = y - x
            dict_x[i['email']] = z.days
        return dict_x
