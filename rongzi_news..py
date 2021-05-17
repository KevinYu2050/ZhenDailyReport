
import execjs
import json
import pandas as pd
import requests
import ast
from datetime import datetime



UNION_ID = "oDeAKQ+7JjDhaBPNN5yeDYHbNBJtOMdy+0m+i2fvHuGAGbdcl144UAZrjuk4uynreJWqqIs6kiQsM8IbOYgM5A==" # Needs to be changed everytime
tag_dict = {
    "企业服务":[],
    "医疗健康":[],
    "生产制造":[],
    "人工智能":[],
    "食品饮料":[],
    "电子商务":[],
    "金融":[],
    "文娱传媒":[],
    "教育培训":[],
    "生活服务":[],
    "服装纺织":[],
    "消费升级":[],
    "先进制造":[],
    "硬科技":[],
    "硬件":[],
    "区块链":[],
    "汽车交通":[],
    "农业":[],
    "批发零售":[],
    "VR/AR":[],
    "社交社区":[],
    "游戏":[],
    "物联网":[]
}

def get_qimingpian_url():
    url =  "https://vipapi.qimingpian.com/DataList/investEventVip"
    page = 0
    df_concat = []
    while page <= 4:
        page += 1
        payload =  {"page":page, "unionid":UNION_ID}
        response = requests.post(url, data=payload)
        res_json = json.loads(response.text)
        # print(res_json)
        decrypt_data = decrypt(res_json["encrypt_data"])
        json_data = json.loads(decrypt_data)["list"]
        # print(pd.DataFrame(json_data))
        df_concat.append(pd.DataFrame(json_data))
        # print(json_data)

    return pd.concat(df_concat)

 
 
def decrypt(encrypt_data):
    ctx = execjs.compile(open('test.js').read())
    return ctx.call('my_decrypt', encrypt_data)

def proc_data(df, date):
    for index, row in df.iterrows():
        ret_string = ""
        date_df = row["time"].replace('.', '')
        if date_df != date:
            pass
        else:
            ret_string += row["yewu"]
            ret_string += "「"
            ret_string += row["product"]
            ret_string += "」"
            ret_string += "完成由"
            
            lingtou = []
            dutou = []
            hetou = []
            gentou = []
            inv_info = ast.literal_eval(row["investor_info"])
            for inv in inv_info:
                if inv["invest_type_name"] == "领投":
                    lingtou.append(inv["investor"])
                elif inv["invest_type_name"] == "跟投":
                    gentou.append(inv["investor"])
                elif inv["invest_type_name"] == "独投":
                    dutou.append(inv["investor"])
                elif inv["invest_type_name"] == "合投":
                    hetou.append(inv["investor"])

            
            ret_string += str_format(lingtou, "领投")
            ret_string += str_format(gentou, "跟投")
            ret_string += str_format(dutou, "独投")
            ret_string += str_format(hetou, "合投")
            ret_string = ret_string[:-2]

            ret_string += "的"
            ret_string += row["money"]
            ret_string += row["jieduan"]
            ret_string += "投资"

            # print(ret_string)
            tag_dict[row["hangye1"]].append(ret_string)

    return tag_dict

def get_36kr_news():
    url = "https://gateway.36kr.com/api/mis/nav/newsflash/flow"
    response = requests.post(url, headers={"content-type": "application/json"}, data=json.dumps({"partner_id":"web","param":{"pageSize":50,"pageEvent":1,"pageCallback":"eyJmaXJzdElkIjoxMjE4MjI0NjkzMzM0NDA1LCJsYXN0SWQiOjEyMTgwNDQzMzE0NjMwNDQsImZpcnN0Q3JlYXRlVGltZSI6MTYyMDYyNjUzNDUwNSwibGFzdENyZWF0ZVRpbWUiOjE2MjA2MTU1MjYwOTB9","siteId":1,"platformId":2}}))
    items = json.loads(response.text)["data"]["itemList"]
    news_list = []

    for item in items:
        content = item["templateMaterial"]["widgetContent"]
        if content.find("融资") == -1:
            news_list.append(content.replace("36氪获悉，", "").replace("截至发稿，",""))

    return news_list

def get_36kr_deep_news():
    url = "https://gateway.36kr.com/api/mis/page/theme/flow"
    response = requests.post(url, headers={"content-type": "application/json"}, data=json.dumps({"partner_id":"web","param":{"itemId": "327690223617","pageSize":1,"pageEvent":1,"pageCallback":"eyJmaXJzdElkIjo5MTEyOTgsImxhc3RJZCI6OTAxMTU2LCJmaXJzdENyZWF0ZVRpbWUiOjE2MDIzMjUyNjk3ODIsImxhc3RDcmVhdGVUaW1lIjoxNTk5Mjc3NjA2MTM2fQ","siteId":1,"platformId":2}}))
    items = json.loads(response.text)["data"]["itemList"]
    news_list = []

    for item in items:
        news_list.append((item["templateMaterial"]["content"], item["templateMaterial"]["itemId"]))

    return news_list



def compile_page(tag_dict, news_list, deep_news):
    page = ""
    page += "**********热门赛道**********\n\n"
    for tag in tag_dict.keys():
        page += "【{}】\n\n".format(tag)
        count = 1
        for line in tag_dict[tag]:
            page += str(count) + ". {}。\n\n".format(line)
            count += 1

    page += "**********大公司新闻**********\n\n"

    count = 1
    for news in news_list:
        page += str(count) + ". {} \n\n".format(news)
        count += 1

    page += "**********深度阅读**********\n\n"
    count = 1
    for news in deep_news:
        page += str(count) + ". {}。\n\n".format(news[0])
        page += "https://www.36kr.com/p/{} \n\n".format(news[1])
        count += 1




    return page


def str_format(li, inv_type):
    if li:
        return "、".join(li) + inv_type + ", "
    else:
        return ""



if __name__ == '__main__':
    date = datetime.today().strftime("%Y%m%d")
    # print(date)

    df_news = get_qimingpian_url()
    df_news.to_csv("./data/{}.csv".format(date))
    df_news = pd.read_csv("./data/{}.csv".format(date))
    tag_dict = proc_data(df_news, date)
    news_list = get_36kr_news() 
    deep_news = get_36kr_deep_news()


    page = compile_page(tag_dict, news_list, deep_news)
    with open("./pages/{}.txt".format(date), "w") as f:
        f.write(page)