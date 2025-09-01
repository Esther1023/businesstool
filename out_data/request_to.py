import requests
import json
import math
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

url = "https://www.jiandaoyun.com/_/data_process/data/find"
count_url='https://www.jiandaoyun.com/_/data_process/data/count'

headers = {
    "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiIzYzAwZGM1Yi05NmI5LTQ1NWYtYTg1OS1jNTI4MGE2NzYwM2UiLCJleHAiOjE3NDMwMDU1MTQsImlhdCI6MTc0MjkxOTExNCwic3ViIjoiMmYyZWYyNTUtNDYyOS00ZDg2LTlkYTQtNWVkOWUzNWJlNjRkIn0.e6lGRB5mv4hN8FDohdp4uWmUt0JL6k7T9uFCvVrx3V0',
    "Access-Control-Allow-Origin": "https://www.jiandaoyun.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Content-Type": "application/json",
    "Cookie": "_csrf=s%3Ax1buOuPe2jqWLMoJqdduXHQk.J8KScwU0EJDOXe6Q0HXe0nhqctFznlfmvWErb1eNc4o; Hm_lvt_de47dd1629940fe88b02865de93dd9fe=1742919042; Hm_lpvt_de47dd1629940fe88b02865de93dd9fe=1742919042; HMACCOUNT=EBF46219D8261D65; auth_token=s%3AeyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NDI5MTkxMTIsImV4cCI6MTc0MzUyMzkxMiwic3ViIjoiNjdlMmQ1YzgxNzk3MmYxZWQwNmNhYjExIiwianRpIjoic2VFNUZKTUFDb3VIU3dnWSJ9.8DsO6GqVNQCzfZqcIkXatNAR2-cnXcnIi0KDAZcz436ThUtiewx-AvqXkQPS1jaElnMoKQ3FI6np3qTK2tQImg.zMWsWmiD2dWpVWHv8H5t49C9pd0qgobTJlJtFAmjFd0; GSuvNKHqfvX2r6v7P8HkZv2bow=s%3AVUjHAVfF7lx606V8FghT8tjw0cAwZjyB.w58IVXUVjdKPQGv86LRTSuO2%2FSdzGi1RcQ9egIdZlSA; JDY_SID=s%3A72DEXQst6QVUTfgUZzA5tq2ZUQDRxVep.JGPwxb177JrwMGn905T%2BIZg58f6zyCQ2pQGMA4rxTFY; fx-lang=zh_cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
    "x-csrf-token": "Rvuz8NOM-LriaGQWE5szdKXxFvxEUU25-A0o",
    "x-jdy-ver": "9.18.5",
    "x-request-id": "9b023f90-2ac3-4033-bae1-b787fd2d396c"
}

count_data = {
  "appId": "5a015dd12d85443cacd1b893",
  "authGroupId": 0,
  "entryId": "5a0186552d85443cacd4ef18",
  "filter": {
    "cond": [],
    "rel": "and"
  },
  "hasLimit": 'true',
  "hasTotalCount": 'true'
}
count_response = requests.post(count_url, headers=headers, json=count_data)
count = count_response.json().get('count')

# 分页查询
page_size = 300
total_pages = math.ceil(count / page_size)
all_data = []
data_list = []
def fetch_page_data(page):
    skip = page * page_size
    data ={
    "appId": "5a015dd12d85443cacd1b893",
    "authGroupId": 0,
    "entryId": "5a0186552d85443cacd4ef18",
    "filter": {
        "cond": [],
        "rel": "and"
    },
    "skip":skip,
    "fields": [
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "用户id-[废弃]",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1547198224989",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "用户ID",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1666084502610",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "辅助-商机编号",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1666084502609",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "商机负责人-辅助",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1681270757648",
        "type": "user"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "发票性质",
        "labelHidden": 'false',
        "lineWidth": 12,
        "name": "_widget_1551867985398",
        "type": "subform",
        "pc_sticky_column": {
            "enable": 'false',
            "limit": 1
        },
        "items": [
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "类型",
            "labelHidden": 'false',
            "name": "_widget_1551867985477",
            "type": "combo",
            "colorEnable": 'false',
            "items": [
                {
                "text": "实施",
                "value": "实施"
                },
                {
                "text": "版本",
                "value": "版本"
                },
                {
                "text": "代采购",
                "value": "代采购"
                },
                {
                "text": "预付款",
                "value": "预付款"
                },
                {
                "text": "版本费（退款）",
                "value": "版本费（退款）"
                },
                {
                "text": "其他",
                "value": "其他"
                },
                {
                "text": "培训费",
                "value": "培训费"
                },
                {
                "text": "数据找回",
                "value": "数据找回"
                },
                {
                "text": "企业微信返佣",
                "value": "企业微信返佣"
                },
                {
                "text": "运维费",
                "value": "运维费"
                },
                {
                "text": "金牌服务费",
                "value": "金牌服务费"
                },
                {
                "text": "钉钉服务商",
                "value": "钉钉服务商"
                },
                {
                "text": "finetube",
                "value": "finetube"
                },
                {
                "text": "九数云",
                "value": "九数云"
                },
                {
                "text": "数跨境",
                "value": "数跨境"
                }
            ],
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "产品线",
            "labelHidden": 'false',
            "name": "_widget_1666263558016",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "订单类别",
            "labelHidden": 'false',
            "name": "_widget_1666263558021",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "订单属性",
            "labelHidden": 'false',
            "name": "_widget_1715667060775",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "订单所属人",
            "labelHidden": 'false',
            "name": "_widget_1715667060819",
            "type": "user",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "订单号",
            "labelHidden": 'false',
            "name": "_widget_1551867985926",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "开票金额",
            "labelHidden": 'false',
            "name": "_widget_1551867985710",
            "type": "number",
            "displayMode": "number",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "订单总金额",
            "labelHidden": 'false',
            "name": "_widget_1666263558020",
            "type": "number",
            "precision": 'null',
            "displayMode": "number",
            "thousandsSeparator": 'false',
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "备注",
            "labelHidden": 'false',
            "name": "_widget_1568603870181",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "用户id",
            "labelHidden": 'false',
            "name": "_widget_1666263558022",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "订单流水号",
            "labelHidden": 'false',
            "name": "_widget_1666263558023",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "订单类型",
            "labelHidden": 'false',
            "name": "_widget_1666263558017",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "商机编号",
            "labelHidden": 'false',
            "name": "_widget_1666263558024",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "是否回款（针对无订单号）",
            "labelHidden": 'false',
            "name": "_widget_1610336841332",
            "type": "radiogroup",
            "colorEnable": 'false',
            "items": [
                {
                "text": "是",
                "value": "是"
                },
                {
                "text": "否",
                "value": "否"
                }
            ],
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "开票订单流水号",
            "labelHidden": 'false',
            "name": "_widget_1651212591677",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "是否关闭开票窗口",
            "labelHidden": 'false',
            "name": "_widget_1574739898896",
            "type": "radiogroup",
            "colorEnable": 'false',
            "items": [
                {
                "text": "是",
                "value": "是"
                },
                {
                "text": "否",
                "value": "否"
                }
            ],
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "测试结果",
            "labelHidden": 'false',
            "name": "_widget_1679017420499",
            "type": "text",
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "实际开票金额（作废清零）",
            "labelHidden": 'false',
            "name": "_widget_1726019092090",
            "type": "number",
            "precision": 'null',
            "displayMode": "number",
            "thousandsSeparator": 'false',
            "subform": "_widget_1551867985398"
            },
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "订单已开金额",
            "labelHidden": 'false',
            "name": "_widget_1726019648005",
            "type": "number",
            "precision": 'null',
            "displayMode": "number",
            "thousandsSeparator": 'false',
            "subform": "_widget_1551867985398"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "识别原件",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1605160124109",
        "type": "image",
        "showStyle": "list"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "识别文本",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1605160124174",
        "type": "textarea"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "客户开票图片信息",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1587347958066",
        "type": "image",
        "showStyle": "list"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "客户开票多行文本",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1587347958081",
        "type": "textarea"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "开票主体",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1540978320544",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "text": "帆软软件有限公司",
            "value": "帆软软件有限公司",
            "selected": 'true'
            },
            {
            "text": "帆软软件有限公司上海分公司",
            "value": "帆软软件有限公司上海分公司"
            },
            {
            "text": "达孜帆软软件有限公司",
            "value": "达孜帆软软件有限公司"
            },
            {
            "text": "台湾帆软有限公司",
            "value": "台湾帆软有限公司"
            },
            {
            "value": "帆软软件有限公司宿迁分公司",
            "text": "帆软软件有限公司宿迁分公司",
            "color": "#00AED1"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "发票类型",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382767",
        "type": "combo",
        "colorEnable": 'false',
        "async": {
            "data": {
            "formId": "636b4b296ed170000a760b80",
            "field": "_widget_1667975978076"
            }
        }
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "普票说明",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1668675683199",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "value": "公司",
            "text": "公司"
            },
            {
            "value": "政府、事业单位、个人",
            "text": "政府、事业单位、个人"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "公司名称",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382781",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "税号",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382794",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "注册地址",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382807",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "注册电话",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382820",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "开户行",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382833",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "账号",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382846",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "发票内容",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382859",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "text": "简道云技术服务费",
            "value": "简道云技术服务费",
            "selected": 'true'
            },
            {
            "text": "技术服务费",
            "value": "技术服务费"
            },
            {
            "text": "培训费",
            "value": "培训费"
            },
            {
            "text": "简道云应用平台[简称:简道云]V4.0",
            "value": "简道云应用平台[简称:简道云]V4.0"
            },
            {
            "text": "简道云应用平台[简称:简道云]V5.0",
            "value": "简道云应用平台[简称:简道云]V5.0"
            },
            {
            "text": "简道云私有云平台V1.0",
            "value": "简道云私有云平台V1.0"
            },
            {
            "value": "FineDataLink大数据处理平台[简称：FineDataLink]V4.0",
            "text": "FineDataLink大数据处理平台[简称：FineDataLink]V4.0",
            "color": "#6AC73C"
            },
            {
            "text": "FineData大数据管理平台V1.6",
            "value": "FineData大数据管理平台V1.6"
            },
            {
            "text": "Technical service",
            "value": "Technical service"
            },
            {
            "text": "九数云技术服务费",
            "value": "九数云技术服务费"
            },
            {
            "text": "其他",
            "value": "其他",
            "isOther": 'true'
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "金额",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382908",
        "type": "number",
        "displayMode": "number"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "其他备注信息",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382898",
        "type": "textarea"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "产品线",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297897339",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "币种",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297897239",
        "type": "combo",
        "colorEnable": 'false',
        "async": {
            "data": {
            "field": "_widget_1656063779144",
            "formId": "62b58723e05fd100083be4e5"
            }
        }
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "套数",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297897726",
        "type": "number",
        "precision": 'null',
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "TW-商品单价（不含税价）",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1666146745739",
        "type": "number",
        "precision": 0,
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "TW-商品总价（不含税价）",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1666146745740",
        "type": "number",
        "precision": 0,
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "TW-营业税金额",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1666146745741",
        "type": "number",
        "precision": 0,
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "合同上传",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297898471",
        "type": "upload"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "开票日汇率",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1672036258337",
        "type": "number",
        "precision": 4,
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "寄送方式",
        "labelHidden": 'false',
        "lineWidth": 4,
        "name": "_widget_1651297897560",
        "type": "radiogroup",
        "colorEnable": 'true',
        "items": [
            {
            "text": "纸质寄送",
            "value": "纸质寄送",
            "color": "#FA5353"
            },
            {
            "text": "电子邮寄发送",
            "value": "电子邮寄发送",
            "color": "#F5C13C"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "是否与合同一起邮寄",
        "labelHidden": 'false',
        "lineWidth": 4,
        "name": "_widget_1586827271030",
        "type": "radiogroup",
        "colorEnable": 'true',
        "items": [
            {
            "text": "否",
            "value": "否",
            "selected": 'true',
            "color": "#FA5353"
            },
            {
            "text": "是",
            "value": "是",
            "color": "#2FCD6E"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "快递费用",
        "labelHidden": 'false',
        "lineWidth": 4,
        "name": "_widget_1542705972888",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "text": "包邮",
            "value": "包邮",
            "widgetsMap": [
                "_widget_1590545557387"
            ],
            "selected": 'true'
            },
            {
            "text": "到付（客户承担）",
            "value": "到付（客户承担）",
            "widgetsMap": []
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "收件人",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1586765820367",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "联系方式",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1586765820539",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "邮寄地址",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1586765820555",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "邮箱",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1555486143873",
        "type": "text",
        "regexType": "email"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "邮箱-多个",
        "labelHidden": 'false',
        "lineWidth": 12,
        "name": "_widget_1704698472728",
        "type": "subform",
        "pc_sticky_column": {
            "enable": 'false',
            "limit": 1
        },
        "items": [
            {
            "id": "5a0186552d85443cacd4ef18",
            "form": "5a0186552d85443cacd4ef18",
            "text": "邮箱",
            "labelHidden": 'true',
            "name": "_widget_1704698472730",
            "type": "text",
            "regexType": "email",
            "subform": "_widget_1704698472728"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "是否已开票",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651737273224",
        "type": "radiogroup",
        "colorEnable": 'true',
        "items": [
            {
            "text": "是",
            "value": "是",
            "color": "#2FCD6E"
            },
            {
            "text": "否",
            "value": "否",
            "color": "#F5C13C"
            },
            {
            "text": "失效",
            "value": "失效",
            "color": "#FA5353"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "开票日期",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1578472947792",
        "type": "datetime",
        "format": "yyyy-MM-dd"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "开票号码",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651737273317",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "是否寄出",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510050042099",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "value": "是",
            "text": "是"
            },
            {
            "selected": 'true',
            "value": "否",
            "text": "否"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "顺丰单号",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382985",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "作废处理日期",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297900514",
        "type": "datetime",
        "format": "yyyy-MM-dd"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "财务作废性质",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297900560",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "红冲发票号码",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297900579",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "申请人",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1583720348797",
        "type": "user"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "录入日期",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382969",
        "type": "datetime",
        "format": "yyyy-MM-dd"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "发票id",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1650520688334",
        "type": "sn"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "发票id（原）--作废",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1574822651338",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "申请人对应商务",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1701141440796",
        "type": "user"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "是否作废",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1575275115379",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "text": "是",
            "value": "是"
            },
            {
            "text": "否",
            "value": "否",
            "selected": 'true'
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "申请作废时间",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651737273623",
        "type": "datetime",
        "format": "yyyy-MM-dd"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "是否寄回旧发票",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651296849505",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "text": "是",
            "value": "是"
            },
            {
            "text": "否",
            "value": "否"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "作废原因",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297900323",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "text": "客户原因导致给错开票信息等",
            "value": "客户原因导致给错开票信息等"
            },
            {
            "text": "自身原因导致写错、未确认等",
            "value": "自身原因导致写错、未确认等"
            },
            {
            "text": "发票本身原因导致客户不能抵扣通过",
            "value": "发票本身原因导致客户不能抵扣通过"
            },
            {
            "text": "财务原因导致发票开错",
            "value": "财务原因导致发票开错"
            },
            {
            "text": "其他",
            "value": "其他",
            "isOther": 'true'
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "作废备注",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651737273124",
        "type": "textarea"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "是否重开发票",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1551867986222",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "text": "是",
            "value": "是"
            },
            {
            "text": "否",
            "value": "否",
            "selected": 'true'
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "重开原因",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651740963515",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "text": "客户原因",
            "value": "客户原因"
            },
            {
            "text": "销售原因",
            "value": "销售原因"
            },
            {
            "text": "财务原因",
            "value": "财务原因"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "作废发票id",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297900119",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "订单号-作废",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382956",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "辅助-日期字段-作废",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1574822651544",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "是否回款-作废",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1510049382919",
        "type": "radiogroup",
        "colorEnable": 'false',
        "items": [
            {
            "value": "是",
            "text": "是"
            },
            {
            "value": "否",
            "text": "否"
            }
        ]
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "申请人-作废",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1547198225534",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "拼接文本-合同用",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1667462816280",
        "type": "textarea"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "辅助-地址",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1681869516777",
        "type": "address",
        "needDetail": 'true'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "辅助-商机责任人判断",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1681270757649",
        "type": "number",
        "precision": 'null',
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "废弃-需要销售承担的快递成本",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1590545557387",
        "type": "number",
        "displayMode": "number"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "开票明细单号校验",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1718788184306",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "合计开票明细金额",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1726020258317",
        "type": "number",
        "precision": 'null',
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "税率",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651737272079",
        "type": "number",
        "precision": 'null',
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "不含税金额",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297898820",
        "type": "number",
        "precision": 2,
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "税额",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1653296128449",
        "type": "number",
        "precision": 2,
        "displayMode": "number",
        "thousandsSeparator": 'false'
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "公司类型",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1651297899971",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "text": "信息组临时用",
        "labelHidden": 'false',
        "lineWidth": 6,
        "name": "_widget_1680055137967",
        "type": "text"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "name": "creator",
        "type": "user",
        "text": "提交人"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "name": "createTime",
        "type": "datetime",
        "format": "yyyy-MM-dd HH:mm:ss",
        "text": "提交时间"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "name": "updateTime",
        "type": "datetime",
        "format": "yyyy-MM-dd HH:mm:ss",
        "text": "更新时间"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "name": "flowState",
        "type": "flowState",
        "text": "流程状态"
        },
        {
        "id": "5a0186552d85443cacd4ef18",
        "form": "5a0186552d85443cacd4ef18",
        "name": "chargers",
        "type": "chargers",
        "text": "当前节点/负责人"
        }
    ],
    "limit": page_size,
    "sort": []
    }
    time.sleep(0.3)  # 增加 0.3 秒的延迟
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        page_data = response.json().get('data', [])
        return page_data
    else:
        return []
        

# 使用线程池并发获取数据
with ThreadPoolExecutor(max_workers=5) as executor:  # 设置最大线程数为 5
    future_to_page = {executor.submit(fetch_page_data, page): page for page in range(total_pages)}
    for future in as_completed(future_to_page):
        page = future_to_page[future]
        try:
            page_data = future.result()
            for item in page_data:
                time.sleep(0.1)
                data_list.append({
                    '_id': item.get('_id', None),
                    '公司名称': item.get('_widget_1510049382781', None),
                    '税号': item.get('_widget_1510049382794', None),
                    '注册地址': item.get('_widget_1510049382807', None),
                    '注册电话': item.get('_widget_1510049382820', None),
                    '开户行': item.get('_widget_1510049382833', None),
                    '账号': item.get('_widget_1510049382846', None),
                    '发票内容': item.get('_widget_1510049382859', None),
                    '开票金额': item.get('_widget_1551867985398', [{}])[0].get('_widget_1551867985710', None) if item.get('_widget_1551867985398') else None
                })
            print(f"已获取第 {page + 1}/{total_pages} 页数据")
        except Exception as e:
            print(f"第 {page + 1} 页处理失败: {e}")

# 创建 DataFrame 并保存为 Excel
df = pd.DataFrame(data_list, dtype="string")
output_file = "output.xlsx"
df.to_excel(output_file, index=False)
print("数据已保存到 output.xlsx")