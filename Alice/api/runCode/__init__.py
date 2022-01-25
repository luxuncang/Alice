import base64
import requests
import json

Language = {
    'php5.3':15,
    'php5.4':16,
    'php5.5':3,
    'php5.6': 17,
    'php7':18,
    'php7.4':37,
    'python2.7':19,
    'python3':20,
    'C#':10,
    'F#':22,
    'java1.7':8,
    'java1.8':23,
    'shell':11,
    'C':7,
    'C++':7,
    'nasm':24,
    'go':6,
    'lua':25,
    'perl': 14,
    'ruby':1,
    'nodejs': 4,
    'Objective-C':12,
    'swift':21,
    'erlang':26,
    'rust': 27,
    'R':28,
    'scala':5,
    'haskell':29,
    'D':30,
    'clojure':2,
    'groovy':31,
    'lisp':32,
    'ocaml': 33,
    'CoffeeScript':35,
    'racket':35,
    'nim':36,
}

def runCode(code, language, stdin=''):
    stdin = '%0A'.join(stdin.strip('\n').split('\n'))

    if not stdin:
        stdin = None
    language = Language[language]
    code = str(base64.b64encode(code.encode("utf-8")), "utf-8")
    url = 'http://runcode-api2-ng.dooccn.com/compile2'
    headers = {'Host': 'runcode-api2-ng.dooccn.com', 'Connection': 'keep-alive', 'Content-Length': '210', 'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Origin': 'http://www.dooccn.com', 'Referer': 'http://www.dooccn.com/', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'}
    cookies = {'Set-CacheRemark': 'default'}
    data = {'language': language, 'code': code, 'stdin': stdin}
    res = requests.post(url, headers=headers,cookies=cookies, data=data).text
    res = json.loads(res)
    return res['output'] + res['errors'].rstrip('\n')
