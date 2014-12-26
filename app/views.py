from django.views.generic import View
from django.http import HttpResponse

class Index(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Django 1.7 on Openshift')
