import json


async def write(a:int):
    with open("main_nps.json", "rb") as r:
        y = json.load(r)
        if a <= 6:
            y["critics"]+=1
        elif a>6 and a<9:
            y["neytral"]+=1
        else:
            y["proms"]+=1
        y["summ"]+=1

    y["procents"] = [round(y["critics"]*100/y["summ"]), round(y["neytral"]*100/y["summ"]), round(y["proms"]*100/y["summ"])]
    y["nps"] = y["procents"][2] - y["procents"][0]
    with open("main_nps.json", "w") as w:
        json.dump(y, w)

    with open("main_nps.json", "rb") as r:
        z = json.load(r)
    print(z)


async def read():
    with open("main_nps.json", "rb") as r:
        y = json.load(r)
        message=f"Количество:\n" \
                f"Критиков {y['critics']}\n" \
                f"Нейтралов {y['neytral']}\n" \
                f"Промоутеров {y['proms']}\n\n" \
                f"Всего {y['summ']}\n\n" \
                f"nps {y['nps']}%"
    return message


async def clear():
    with open("main_nps.json", "rb") as r:
        y = json.load(r)
        y["critics"] = 0
        y["neytral"] = 0
        y["proms"] = 0
        y["summ"] = 0
        y["procents"] = [0, 0, 0]
        y["nps"] = 0

    with open("main_nps.json", "w") as w:
        json.dump(y, w)

    return await read()
