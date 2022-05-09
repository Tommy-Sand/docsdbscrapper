
from django.http import HttpResponse, Http404
from django.template import loader
from .models import semester
# Create your views here.
def index(request):
    try:
        semesters_list = [i.sem_name[26:len(i.sem_name)-7] for i in semester.objects.all()]
    except:
        raise Http404("Semesters could not be found")
    semesters_list.insert(0, "<Please pick a semester>")
    template = loader.get_template('index.html')
    context = {'Semesters': semesters_list}
    return HttpResponse(template.render(context, request))