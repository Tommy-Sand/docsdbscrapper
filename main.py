from os import remove
from bs4 import BeautifulSoup as BS
import requests
import pymongo

def removeacronym(element):
    if(isinstance(element, str)):
        return element
    if (len(element.contents) > 0):
        temp = element.contents[0]
    else:
        temp = None
    return temp

def search_diclist(diclist, key):
    for i in range(len(diclist)):
        if(diclist[i].get(key, -1) != -1):
            return (diclist[i][key], i)
    return -1

class course:
    def __init__(self, cid, cname):
        self.cid = cid
        self.cname = cname
        self.lec = []
        self.mostrecent = []

def createcourse(curcourse, table, date,columnnames):
    rows = table.find_all("tr")
    for i in rows:
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
                temp = list(map(removeacronym, temp))
                lecture.append(temp)
            else:
                lecture.append(None)
        if(islab):
            continue
        copylecture = lecture.copy()
        if(len(lecture) == 10):
            del lecture[1:4]
            del copylecture[1:4]
            for i in range(1, len(lecture) - 1):
                try:
                    copylecture[i] = {columnnames[i]: [{date: int(lecture[i])}]}
                    lecture[i] = {columnnames[i]: int(lecture[i])}
                except TypeError:
                    copylecture[i] = {columnnames[i]: [{date: lecture[i]}]}
                    lecture[i] = {columnnames[i]: lecture[i]}
        if(lecture != []):
            if(isinstance(lecture[0],list)):
                lecture[0] = [i for i in lecture[0] if i != None]
                for i in range(len(lecture[0])):
                    lecture[0][i] = lecture[0][i].strip("\n\t")
                lecture[0] = " ".join(lecture[0])
            curcourse.lec.append({lecture[0]:copylecture[1:]})
            curcourse.mostrecent.append({lecture[0]:lecture[1:len(lecture)-1]})

def createdb():
    content = requests.get("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False).text
    BScontent = BS(content,"html.parser")
    date = BScontent.find("h5").contents[0].strip()
    courses = BScontent.find_all("h2")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    enrollment = myclient["Enrollment"]
    if (BScontent.find("head").find("title").contents[0].strip() in enrollment.list_collection_names()):
        return
    semester = enrollment[BScontent.find("head").find("title").contents[0].strip()]
    ccourses = [course(i.find("a")["id"], i.contents[1]) for i in courses]
    columnnames = list(map(removeacronym, courses[0].find_next_sibling("table").find("tr").find_all("th")))
    del columnnames[1:4]
    for i in range(len(courses)):
        table = courses[i].find_next_sibling("table")
        createcourse(ccourses[i],table, date, columnnames)
        semester.insert_one({"cid": ccourses[i].cid, "cname": ccourses[i].cname, "lectures": ccourses[i].lec, "most recent": ccourses[i].mostrecent})
    return

def updatedb():
    content = requests.get("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False).text
    BScontent = BS(content,"html.parser")
    date = BScontent.find("h5").contents[0].strip()
    courses = BScontent.find_all("h2")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    enrollment = myclient["Enrollment"]
    semester = enrollment[BScontent.find("head").find("title").contents[0].strip()]
    ccourses = [course(i.find("a")["id"], i.contents[1]) for i in courses]
    columnnames = list(map(removeacronym, courses[0].find_next_sibling("table").find("tr").find_all("th")))
    del columnnames[1:4]
    for i in range(len(courses)):
        table = courses[i].find_next_sibling("table")
        createcourse(ccourses[i],table, date, columnnames)
        db_course = semester.find_one({"cid": ccourses[i].cid})
        if(len(list(db_course)) == 0 ):
            semester.insert_one({"cid": ccourses[i].cid, "cname": ccourses[i].cname, "lectures": ccourses[i].lec, "most recent": ccourses[i].mostrecent})
        elif(ccourses[i].mostrecent != db_course["most recent"]):
            for j in ccourses[i].mostrecent:
                key = list(j.keys())[0]
                if(j[key] == search_diclist(db_course["most recent"], key)[0]):
                    continue
                else:
                    if(j[key] == []):
                        break
                    new = j[key]
                    old = search_diclist(db_course["most recent"], key)[0]
                    for k in new:
                        key2 = list(k.keys())[0]
                        result = search_diclist(old, key2)[0]
                        if(result != -1):
                            if(search_diclist(new, key2)[0] == result):
                                continue
                            else:
                                temp = search_diclist(db_course["lectures"],key)
                                temp2 = search_diclist(temp[0], key2)
                                old[search_diclist(new, key2)[1]] = {key2: search_diclist(new,key2)[0]}
                                temp2[0].append(search_diclist(search_diclist(ccourses[i].lec,key)[0], key2)[0][0])
                                semester.replace_one({"_id" : db_course["_id"]},db_course)
    return

rhead = requests.head("https://docsdb.cs.ualberta.ca/Timetable/1780.html", verify = False)
update = False
with open("etag.txt") as etag:
    if(rhead.headers["Etag"] != etag.readline().strip("\n")):
        update = True

if update:
    with open("etag.txt", "w") as etag:
        etag.write(rhead.headers["Etag"])

createdb()
updatedb() #make sure to tab this so it only updates when needed
