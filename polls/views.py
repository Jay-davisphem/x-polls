from django.db.models import Q
from django.views import generic
from .models import Question, Choice
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

'''
# HARD WAY FUNCTIONAL VIEWS

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list, }
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):              
    question = get_object_or_404(Question, pk=question_id)        
    return render(request, 'polls/results.html', {'question': question})    
'''


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    # Redisplay the question voting form.
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {'question': question, 'error_message': "You didn't select a choice.", })
    else:
        selected_choice.votes += 1
        # Always return an HttpResponseRedirect after successfully dealing # with POST data. This prevents data from being posted twice if a # user hits the Back button.
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


# GENERIC CLASS BASED VIEW BECAUSE OF COMMON FUNCTIONALITIES BETWEEN index, detail and results


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        if self.request.user.is_staff:
            return Question.objects.all().order_by('-pub_date')
        return Question.objects.exclude(pub_date__gt=timezone.now()).exclude(choice=None).order_by('-pub_date')
        #Question.objects.filter(~Q(choice=None), pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Question.objects.all().order_by('-pub_date')
        return Question.objects.exclude(pub_date__gt=timezone.now()).exclude(choice=None)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Question.objects.all().order_by('-pub_date')
        return Question.objects.exclude(pub_date__gt=timezone.now()).exclude(choice=None)
