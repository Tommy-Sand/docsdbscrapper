import requests

rhead = None

try:
    rhead = requests.head("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False)
except:
    print("Warning: Unsecure")

print(rhead)