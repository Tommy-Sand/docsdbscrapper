
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template import loader
from .models import semester
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

def submit(request):
    requested_sem = request.GET['Semester'] + " " + request.GET['Year']
    try:
        chosen_sem = get_object_or_404(semester, sem_name = requested_sem)
    except:
        return HttpResponse("Not Found")
    temp = chosen_sem.courses[0]["lectures"][0]
    dates_list = list(set([i['date'] for i in (temp["Cap"] + temp["Reg"] + temp["With"] + temp["Combd"])]))
    dates_list_2 = [parser.parse(i) for i in dates_list]
    dates_list = [i for _,i in sorted(zip(dates_list_2, dates_list))]
    curr_date = datetime.now()
    dates_list.append(curr_date.isoformat())
    cap_dic = {i['date']: i['num'] for i in temp["Cap"]}
    reg_dic = {i['date']: i['num'] for i in temp["Reg"]}
    with_dic = {i['date']: i['num'] for i in temp["With"]}
    cur_dic = {i['date']: i['num'] for i in temp["Cur"]}
    combd_dic = {i['date']: i['num'] for i in temp["Combd"]}
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