import re,requests

proxies = {
    "http": "socks5://127.0.0.1:12345",
}

def index(address):
    print(address)
    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    q = f"amazon data center in {address}"
    oq = f"amazon data center in {address}"
    url=f"googlemap url"+q+oq
    resp=requests.get(url,headers=headers,proxies=proxies)
    print(resp.text.encode("UTF-8"))
    dir=re.compile('null,null,(?P<dire>(?:[-+]?[1-9]\\d*|[-+]?0)\\.\\d*,(?:[-+]?[1-9]\\d*|[-+]?0)\\.\\d*)]')
    o=dir.finditer(str(resp.text.encode("UTF-8")))
    list1=['']*100
    n=0
    for i in o:
        num=0
        for j in list1:
            if i.group("dire")==j:
                num=1
                break
        if num==0:
            list1[n]=i.group("dire")
            n+=1
    return list1



file=open('Google cloud region.txt','r')
wfile=open('Google cloud RegionAll.txt','w')


listRegion=file.readlines()
for i in listRegion:
    dir=i.split("\n")[0]
    Addresslist=index(dir)
    wfile.write(dir+" ")
    for j in Addresslist:
        if j!='':
            wfile.write(j+' ')
    wfile.write('\n')
