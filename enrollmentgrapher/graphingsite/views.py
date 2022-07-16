
from tkinter.colorchooser import Chooser
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template import loader
from .models import lecture, semester
import json
from datetime import datetime
from dateutil import parser
# Create your views here.

def index(request):
    try:
        years_list = list(set([int(i.sem_name.split()[1]) for i in semester.objects.all()]))
    except:
        raise Http404("Semesters could not be found")
    years_list.insert(0, "<Please pick a Year>")
    semesters_list = ["<Please pick a Semester>", "Fall", "Winter", "Spring", "Summer"]
    template = loader.get_template('semester.html')
    context = {'Years': years_list, "Semesters": semesters_list}
    return HttpResponse(template.render(context, request))

def submit_s(request):
    requested_sem = request.GET['Semester'] + " " + request.GET['Year']
    try:
        chosen_sem = get_object_or_404(semester, sem_name = requested_sem)
    except:
        return HttpResponse("Not Found")
    course_list = [i["cname"] for i in chosen_sem.courses]
    course_list.insert(0, "<Please pick a Course>")
    template = loader.get_template('course_list.html')
    context = { 'courses': course_list}
    return HttpResponse(template.render(context, request))

def submit_s_c(request):
    requested_course = request.GET['course']
    requested_sem = requested_course.split()[2] + ' ' + requested_course.split()[3]
    try:
        chosen_sem = get_object_or_404(semester, sem_name = requested_sem)
    except:
        return HttpResponse("Semester Not Found")
    course = None
    for i in chosen_sem.courses:
        if(requested_course == i["cname"]):
            course = i
    if(course == None):
        raise Http404("Course not found")
    lectures = [i["Lecture"] for i in course["lectures"]]
    template = loader.get_template('lecture_list.html')
    context = {'lectures': lectures, "course": request.GET['course']}
    return HttpResponse(template.render(context, request))

def submit_s_c_l(request):
    requested_course = request.GET['course']
    requested_sem = requested_course.split()[2] + ' ' + requested_course.split()[3]
    try:
        chosen_sem = get_object_or_404(semester, sem_name = requested_sem)
    except:
        return HttpResponse("Not Found")
    course = None
    for i in chosen_sem.courses:
        if(requested_course == i["cname"]):
            course = i['lectures']
    if(course == None):
        raise Http404("Course not found")
    lecture = None
    for i in course:
        if(request.GET['lecture'] == i["Lecture"]):
            lecture = i
    if(lecture == None):
        raise Http404("Lecture not found")
    dates_list = list(set([i['date'] for i in (lecture["Cap"] + lecture["Reg"] + lecture["With"] + lecture["Combd"])]))
    dates_list_2 = [parser.parse(i) for i in dates_list]
    dates_list = [i for _,i in sorted(zip(dates_list_2, dates_list))]
    curr_date = datetime.now()
    dates_list.append(curr_date.isoformat())
    cap_dic = {i['date']: i['num'] for i in lecture["Cap"]}
    reg_dic = {i['date']: i['num'] for i in lecture["Reg"]}
    with_dic = {i['date']: i['num'] for i in lecture["With"]}
    cur_dic = {i['date']: i['num'] for i in lecture["Cur"]}
    combd_dic = {i['date']: i['num'] for i in lecture["Combd"]}
    for i in range(len(dates_list)):
        if cap_dic.get(dates_list[i], -1) == -1:
            cap_dic[dates_list[i]] = cap_dic[dates_list[i-1]]
        if reg_dic.get(dates_list[i], -1) == -1:
            reg_dic[dates_list[i]] = reg_dic[dates_list[i-1]]
        if with_dic.get(dates_list[i], -1) == -1:
            with_dic[dates_list[i]] = with_dic[dates_list[i-1]]
        if cur_dic.get(dates_list[i], -1) == -1:
            cur_dic[dates_list[i]] = cur_dic[dates_list[i-1]]
        if combd_dic.get(dates_list[i], -1) == -1:
            combd_dic[dates_list[i]] = combd_dic[dates_list[i-1]]
    context = {
        "course_name" : json.dumps({"name": requested_course + request.GET['lecture']}),
        "date_list": json.dumps(dates_list),
        "cap_list": json.dumps(list(cap_dic.values())),
        "reg_list": json.dumps(list(reg_dic.values())),
        "with_list": json.dumps(list(with_dic.values())),
        "cur_list": json.dumps(list(cur_dic.values())),
        "combd_list": json.dumps(list(combd_dic.values()))
    }
    template = loader.get_template('chart.html')
    return HttpResponse(template.render(context, request))

if __name__ == "__main__":
    index()