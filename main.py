from turtle import update
from unittest import skip
import requests


def updatedb():
    pass

rhead = requests.head("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False)

with open("etag.txt") as etag:
    if(rhead.headers["Etag"] != etag.readline().strip("\n")):
        update = True

if update:
    with open("etag.txt", "w") as etag:
        etag.write(rhead.headers["Etag"])

    updatedb()