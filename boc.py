import requests
import time
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

data_list = "["
baseUrl = 'http://www.bankofchina.com/sourcedb/operations%sindex%s.htm'
proAndCity = []
#代理
proxiesIps = []
#随机请求头
ua = UserAgent(verify_ssl=False)

def getData(add, totalPage, proxiesIp):
    for page in range(totalPage):
        url = ''
        headers={"User-Agent":ua.random}
        proxies=proxiesIps[random.randint(0, len(proxiesIps)-1)]
        print('ip:'+proxies)
        time.sleep(1)
        if page > 0:
            url = baseUrl %(add, "_"+str(page))
        else:
            url = baseUrl %(add, "")
        req = requests.get(url,headers=headers,proxies=proxies,timeout=10)
        req.encoding = 'utf-8'
        soup = BeautifulSoup(req.text, 'html.parser')
        tables = soup.findAll('table')
        table = tables[1]
        #enumerate()函数将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标
        for trs, tr in enumerate(table.findAll('tr')):
            if trs != 0:
                tds = tr.findAll('td')
                name = tds[0].string
                address = tds[1].string.split()
                postCode = tds[3].string
                if len(address) > 1:
                    data_list += "{\"bankName\":\"" + name + "\",\"city\":\"" + address[0] + "\",\"area\":\"" + address[1] + "\",\"postCode\":\"" + postCode[-7:-1] + "\"},"
                else:
                    data_list += "{\"bankName\":\"" + name + "\",\"city\":\"\",\"area\":\"" + address[0] + "\",\"postCode\":\"" + postCode[-7:-1] + "\"},\n"

def getTotalPage(add):
    url = baseUrl %(add, "")
    req = requests.get(url, {'User-Agent':ua.random})
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup.find(class_='turn_page').p.span.string

def getProAndCity():
    url = "http://www.bankofchina.com/sourcedb/operations/"
    req = requests.get(url, {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'},timeout=10)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, 'html.parser')
    aS = soup.find_all(class_='hui12_20_hover')
    for a in aS:
        proAndCity.append(a['href'][1:])

def getProxies():
    url = "https://www.xicidaili.com/wt/1"
    req = requests.get(url, {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'},timeout=10)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, 'html.parser')
    ips = soup.find_all('tr')
    for tr in ips:
        tds = tr.findAll('td')
        proxiesIps.append({'http': tds[1].string+':'+tds[2]})
    
    
getProAndCity()
print(proAndCity)
print('-----------------------------------------------')
getProxies()
print(proxiesIps)
for add in proAndCity:
    print(add)
    totalPage = getTotalPage(add)
    getData(add, totalPage)
data_list = data_list[:-1]
data_list += ']'
print(data_list)
