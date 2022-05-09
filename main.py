from bs4 import BeautifulSoup as BS
import requests
import pymongo

def removeacronym(element):
    if(isinstance(element, str)):
        return element
    if (len(element.contents) > 0):
        return element.contents[0]
    else:
        return None

def search_diclist(diclist, key, value):
    for i in range(len(diclist)):
        if(diclist[i].get(key, "") == value):
            return (diclist[i], i)
    return {}

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
            if(len(ii.contents) >= 1):
                if("LAB" in ii.contents[0]):
                    islab = True
                    break
                lecture.append(ii.contents[0])
            elif(len(ii.contents) > 1):
                lecture.append(list(map(removeacronym, ii.contents)))
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
                    copylecture[i] = {columnnames[i]: [{"date": date, "num": int(lecture[i])}]}
                    lecture[i] = {columnnames[i]: int(lecture[i])}
                except TypeError:
                    copylecture[i] = {columnnames[i]: [{"date": date, "num": lecture[i]}]}
                    lecture[i] = {columnnames[i]: lecture[i]}
        if(lecture != [] and 'Cancelled' not in lecture):
            if(isinstance(lecture[0],list)):
                lecture[0] = [i for i in lecture[0] if i != None]
                for i in range(len(lecture[0])):
                    lecture[0][i] = lecture[0][i].strip("\n\t")
                lecture[0] = " ".join(lecture[0])
            curcourse.lec.append({
                "Lecture" : lecture[0],
                "Instructor": copylecture[6],
                "Cap": copylecture[1]["Cap"],
                "Reg": copylecture[2]["Reg"],
                "With": copylecture[3]["With"],
                "Cur": copylecture[4]["Cur"],
                "Combd": copylecture[5]["Combd"]
                })
            curcourse.mostrecent.append({
                "Lecture": lecture[0],
                "Cap": lecture[1]["Cap"],
                "Reg": lecture[2]["Reg"],
                "With": lecture[3]["With"],
                "Cur": lecture[4]["Cur"],
                "Combd": lecture[5]["Combd"]
                })
        elif(lecture == []):
            pass
        elif('Cancelled' in lecture):
            pass

def createdb(client, link):
    content = requests.get(link, verify = False).text
    BScontent = BS(content,"html.parser")
    date = BScontent.find("h5").contents[0].strip()
    courses = BScontent.find_all("h2")
    enrollment = client["sample"]["graphingsite_semester"]
    sem_name = BScontent.find("head").find("title").contents[0].strip()
    if (sem_name in enrollment.distinct("semester")):
        return
    ccourses = [course(i.find("a")["id"], i.contents[1]) for i in courses]
    columnnames = list(map(removeacronym, courses[0].find_next_sibling("table").find("tr").find_all("th")))
    array_of_courses = []
    del columnnames[1:4]
    for i in range(len(courses)):
        table = courses[i].find_next_sibling("table")
        createcourse(ccourses[i],table, date, columnnames)
        array_of_courses.append({"cid": ccourses[i].cid, "cname": ccourses[i].cname, "lectures": ccourses[i].lec, "most_recent": ccourses[i].mostrecent})
    enrollment.insert_one({"link": link, "sem_name": sem_name, "courses": array_of_courses})
    return

def updatedb(client, link):
    content = requests.get(link, verify = False).text
    BScontent = BS(content,"html.parser")
    date = BScontent.find("h5").contents[0].strip()
    courses = BScontent.find_all("h2")
    enrollment = client["sample"]["graphingsite_semester"]
    sem_name = BScontent.find("head").find("title").contents[0].strip()
    semester = enrollment.find_one({"sem_name": sem_name})["courses"]
    ccourses = [course(i.find("a")["id"], i.contents[1]) for i in courses]
    columnnames = list(map(removeacronym, courses[0].find_next_sibling("table").find("tr").find_all("th")))
    del columnnames[1:4]
    for i in range(len(courses)):
        table = courses[i].find_next_sibling("table")
        createcourse(ccourses[i],table, date, columnnames)
        db_course = None
        for l in range(len(semester)):
            if(semester[l]["cid"] == ccourses[i].cid):
                db_course = semester[l]
                break
        if(db_course == None ):
            storage_course = {"cid": ccourses[i].cid, "cname": ccourses[i].cname, "lectures": ccourses[i].lec, "most_recent": ccourses[i].mostrecent}
            enrollment.update_one({"sem_name": sem_name}, {"$push":  {"courses": storage_course}})
        elif(ccourses[i].mostrecent != db_course["most_recent"]):
            for j in ccourses[i].mostrecent:
                key = j['Lecture']
                if(j == search_diclist(db_course["most_recent"], 'Lecture', key)[0]):
                    continue
                else:
                    new = j
                    old = search_diclist(db_course["most_recent"], 'Lecture', key)[0]
                    for k in new:
                        result = old.get(k, -1)
                        if(result != -1):
                            if(new.get(k, -1) == result):
                                continue
                            else:
                                temp = search_diclist(db_course["lectures"], 'Lecture', key)
                                search_string = "courses.{}.lectures.{}.{}".format(l, temp[1], k)
                                new_object = {'date': date, 'num': new[k]}
                                enrollment.update_one({"sem_name" : sem_name}, {'$push': {search_string: new_object}})
                                search_string = "courses.{}.most_recent.{}.{}".format(l, temp[1], k)
                                new_value = new_object["num"]
                                enrollment.update_one({"sem_name" : sem_name}, {'$set': {search_string: new_value}})
    return

meta_content = requests.get("https://docsdb.cs.ualberta.ca/", verify = False).text
BSmeta_content = BS(meta_content, "html.parser")
links = [link.get("href") for link in BSmeta_content.find_all('a') if link.get("href").split("/")[-1].strip(".html").isnumeric()]

client = pymongo.MongoClient("mongodb://localhost:27017")
enrollment = client["sample"]["graphingsite_semester"]
etag_coll = client["sample"]["graphingsite_etag"]
for link in links:
    rhead = requests.head(link, verify = False)
    update = False
    if(etag_coll.find_one({"link": link}) == None):
        createdb(client, link)
        etag_coll.insert_one({"link": link, "etag": rhead.headers["Etag"]})
    elif(rhead.headers["Etag"] != etag_coll.find_one({"link": link})['etag']):
        update = True
    if update:
        etag_coll.replace_one({"link": link}, {"link": link, "etag": rhead.headers["Etag"]})
        updatedb(client, link)