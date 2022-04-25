import requests

rhead = None

rhead = requests.head("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False)


with open("etag.txt") as etag:
    print(rhead.headers["Etag"])