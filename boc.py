import requests
import time
import random
import re
import socket
import threading
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

data_list = "["
baseUrl = 'http://www.bankofchina.com/sourcedb/operations%sindex%s.htm'
proAndCity = []
# 代理
proxiesIps = []
# 可用代理
proxiesIpCheckeds = []
# 可用代理的个数
available_table = [] 
# 随机请求头
ua = UserAgent(verify_ssl=False)


def getData(add, totalPage, proxiesIp):
    for page in range(totalPage):
        url = ''
        headers = {"User-Agent": ua.random}
        proxies = proxiesIps[random.randint(0, len(proxiesIps)-1)]
        print('ip:'+proxies)
        time.sleep(1)
        if page > 0:
            url = baseUrl % (add, "_"+str(page))
        else:
            url = baseUrl % (add, "")
        while True:
            try:
                req = requests.get(url, headers=headers, proxies=proxies, timeout=10)
                break
            except requests.exceptions.ConnectionError:
                print('ConnectionError -- please wait 3 seconds')
                time.sleep(3)
            except requests.exceptions.ChunkedEncodingError:
                print('ChunkedEncodingError -- please wait 3 seconds')
                time.sleep(3)
            except req.raise_for_status:
                print('Request error -- please wait 3 seconds')
                time.sleep(3)
            except:
                print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
                time.sleep(3)
        
        req.encoding = 'utf-8'
        soup = BeautifulSoup(req.text, 'html.parser')
        tables = soup.findAll('table')
        table = tables[1]
        # enumerate()函数将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标
        for trs, tr in enumerate(table.findAll('tr')):
            if trs != 0:
                tds = tr.findAll('td')
                name = tds[0].string
                address = tds[1].string.split()
                postCode = tds[3].string
                if len(address) > 1:
                    data_list += "{\"bankName\":\"" + name + "\",\"city\":\"" + \
                        address[0] + "\",\"area\":\"" + address[1] + \
                        "\",\"postCode\":\"" + postCode[-7:-1] + "\"},"
                else:
                    data_list += "{\"bankName\":\"" + name + "\",\"city\":\"\",\"area\":\"" + \
                        address[0] + "\",\"postCode\":\"" + \
                        postCode[-7:-1] + "\"},\n"


def getTotalPage(add):
    url = baseUrl % (add, "")
    req = requests.get(url, {'User-Agent': ua.random})
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup.find(class_='turn_page').p.span.string


def getProAndCity():
    url = "http://www.bankofchina.com/sourcedb/operations/"
    while True:
        try:
            req = requests.get(url, {'User-Agent': ua.random}, timeout=10)
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            time.sleep(3)
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            time.sleep(3)
        except req.raise_for_status:
            print('Request error -- please wait 3 seconds')
            time.sleep(3)
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
            time.sleep(3)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, 'html.parser')
    aS = soup.find_all(class_='hui12_20_hover')
    for a in aS:
        proAndCity.append(a['href'][1:])

def getProxies():
    patternIP = re.compile(r'(?<=<td>)[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}')
    patternPORT = re.compile(r'(?<=<td>)[\d]{2,5}(?=</td>)')
    url = "https://www.xicidaili.com/wt"
    headers = {'User-Agent': ua.random}
    while True:
        try:
            req = requests.get(url, headers=headers, timeout=10)
            break
        except requests.exceptions.ConnectionError:
            print('ConnectionError -- please wait 3 seconds')
            time.sleep(3)
        except requests.exceptions.ChunkedEncodingError:
            print('ChunkedEncodingError -- please wait 3 seconds')
            time.sleep(3)
        except req.raise_for_status:
            print('Request error -- please wait 3 seconds')
            time.sleep(3)
        except:
            print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
            time.sleep(3)
    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, 'html.parser')
    findIP = re.findall(patternIP, str(soup))
    findPORT = re.findall(patternPORT, str(soup))
    for i in range(len(findIP)):
        proxiesIps.append({'http': findIP[i] + ":" + findPORT[i]})
    mul_thread_check('http://www.bankofchina.com/sourcedb/operations/')
    return proxiesIpCheckeds

def check_one(url_check,i):
    #get lock
    lock = threading.Lock()
    #setting timeout
    socket.setdefaulttimeout(8)
    try:
        req = requests.get(url, proxies=proxiesIps[i], headers={'User-Agent':ua.random}, timeout=10)
        lock.acquire()
        print(proxiesIps[i] + 'is OK')
        #get available ip index
        available_table.append(i)
        lock.release()
    except req.raise_for_status:
        lock.acquire()
        print('error')
        lock.release()
 
def mul_thread_check(url_mul_check):
    threads = []
    for i in range(len(proxiesIps)):
        #creat thread...
        thread = threading.Thread(target=check_one, args=[url_mul_check,i,])
        threads.append(thread)
        thread.start()
        print("new thread start" + str(i))
 
    for thread in threads:
        thread.join()
 
    #get the proxiesIpCheckeds[]
    for error_cnt in range(len(available_table)):
        aseemble_ip = {'http': proxiesIps[available_table[error_cnt]]}
        proxiesIpCheckeds.append(aseemble_ip)
    print("available proxy ip:" + str(len(available_table)))

getProxies()
print(proxiesIps)
print('-----------------------------------------------')
getProAndCity()
print(proAndCity)

for add in proAndCity:
    print(add)
    totalPage = getTotalPage(add)
    getData(add, totalPage)
data_list = data_list[:-1]
data_list += ']'
print(data_list)
