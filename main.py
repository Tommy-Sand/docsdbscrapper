from bs4 import BeautifulSoup as BS
import requests


def updatedb():
    #content = requests.get("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False).text
    content = open("content.txt", "r").read()
    BScontent = BS(content,"html.parser")
    courses = BScontent.find_all("h2")
    enroll = BScontent.find_all("table")
    print(enroll[1])
    return

rhead = requests.head("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False)
update = False
with open("etag.txt") as etag:
    if(rhead.headers["Etag"] != etag.readline().strip("\n")):
        update = True

if update:
    with open("etag.txt", "w") as etag:
        etag.write(rhead.headers["Etag"])

updatedb() #make sure to tab this so it only updates when needed