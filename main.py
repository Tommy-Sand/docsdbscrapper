from datetime import date
from tokenize import String
from unittest import skip
from bs4 import BeautifulSoup as BS
from matplotlib.pyplot import table
import requests
import pymongo

def remove_acronym(element):
    if(isinstance(element, str)):
        return element
    if (len(element.contents) > 0):
        temp = element.contents[0]
    else:
        temp = None
    return temp

class course:
    def __init__(self, cid, cname):
        self.courseid = cid
        self.cname = cname
        self.lec = []

def createcourse(curcourse, table, date):
    columns = table.find_all("tr")
    for i in columns:
        lecture = []
        islab = False
        for ii in i.find_all("td"):
            if(len(ii.contents) == 1):
                if("LAB" in ii.contents[0]):
                    islab = True
                    break
                lecture.append(ii.contents[0])
            elif(len(ii.contents) > 1):
                temp = ii.contents
                temp = list(map(remove_acronym, temp))
                lecture.append(temp)
            else:
                lecture.append(None)
        if(islab):
            continue
        if(lecture != []):
            curcourse.lec.append(lecture)
        if(len(lecture) == 10):
            del lecture[1:4]
            lecture.append(date)


def createdb():
    #content = requests.get("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False).text
    content = open("content.txt", "r").read()
    BScontent = BS(content,"html.parser")
    date = BScontent.find("h5").contents[0]
    courses = BScontent.find_all("h2")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    enrollment = myclient["Enrollment"]
    if (BScontent.find("head").find("title").contents[0] in enrollment.list_collection_names()):
        return
    semester = enrollment[BScontent.find("head").find("title").contents[0]]
    ccourses = [course(i.find("a")["id"], i.contents[1]) for i in courses]
    for i in range(len(courses)):
        table = courses[i].find_next_sibling("table")
        createcourse(ccourses[i],table, date)
        semester.insert_one({ccourses[i].courseid: ccourses[i].lec})
    return

def updatedb():
    #content = requests.get("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False).text
    content = open("content.txt", "r").read()
    BScontent = BS(content,"html.parser")
    date = BScontent.find("h5")
    courses = BScontent.find_all("h2")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    if("Enrollment" not in myclient.list_database_names()):
        enrollment = myclient["Enrollment"]
    test = courses[1].find_next_sibling("table")
    return

rhead = requests.head("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False)
update = False
with open("etag.txt") as etag:
    if(rhead.headers["Etag"] != etag.readline().strip("\n")):
        update = True

if update:
    with open("etag.txt", "w") as etag:
        etag.write(rhead.headers["Etag"])

#updatedb() #make sure to tab this so it only updates when needed
createdb()