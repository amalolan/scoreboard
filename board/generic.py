from django.shortcuts import get_object_or_404
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.views.generic import View
from .models import *
import json


class QueryView(View):
    """
    Every time a form is submitted in board:manager, a post request is made with
    those input values.
    TODO: Documentation
    """
    model = Scoreboard
    error_msg = "ERROR: An exception has occurred on the server."
    success_status = 200
    error_status = 500
    
    def get_success_msg(self, request, result):
        return "Successfully reached QueryView for Scoreboard" + ". NOTE: " + \
               "REQUEST WITH NAME '" + request.POST['name'] + "' is " + \
               "STILL USING " + "QueryView.get_success_msg()."
    
    def post_handler(self, request, model_instance):
        raise ImproperlyConfigured(
            "Post handler is not set. Please define the post_handler "
            "function which should return the model's POST request handler")
    
    def post(self, request, pk):
        """
        request.POST contains the data of the submitted form in board:manager.
        :return: HttpResponse with a success or failure message
        """
        msg, status = '', 500
        try:
            model_instance = get_object_or_404(self.model, pk=pk)
            result = self.post_handler(request, model_instance)
            model_instance.save()
            msg = self.get_success_msg(request, result)
            status = self.success_status
        except Exception as e:
            msg = self.error_msg + " Exception Message: " + str(e)
            status = self.error_status
            print(str(e))
            raise e
        finally:
            return HttpResponse(json.dumps({'msg': msg}), status=status)
