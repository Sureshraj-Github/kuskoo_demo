from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView, UpdateView, CreateView, DetailView
from .api_call import call_post_method_without_token_app_builder,call_get_method,call_get_method_without_token,call_post_with_method,call_post_method_for_without_token,call_delete_method,call_delete_method_without_token, call_put_method,call_put_method_without_token
import requests
import json
from django.contrib import messages
from django.urls import resolve, reverse
import jwt
from django.contrib.auth import logout
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from .forms import *
from rest_framework import status
from rest_framework.response import Response
from django.contrib import messages
from django.conf import settings
from .api_call import *
from functools import wraps
BASEURL = settings.BASEURL

api_url= BASEURL + '/api/token/verify/'

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the session variable exists
        if  'user_token' not in request.session:
            return redirect('login')
        # Verify token validity
        token = request.session['user_token']
        print('token',token)
        headers = {
        'Content-Type': 'application/json',
        }
        json_data = {
            'token': token
        }
        response = requests.post(api_url, data=json.dumps(json_data),headers=headers)
        print('response',response.status_code)
        if response.status_code != 200:
            # Token is invalid or expired
            del request.session['user_token']
            return redirect('login')
        # Token is valid, proceed with the view
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

BASEURL = 'http://127.0.0.1:9000/'

def base_dashboard(request):
    return render(request, 'base_dashboard.html')

def login(request):
    try:
        # Check if the request method is POST
        if request.method == "POST":
            username = request.POST.get('email')
            password = request.POST.get('password')
            payload = {        
                "username" : username,
                "password" : password
            }
            # Convert payload to JSON format
            json_payload = json.dumps(payload)
            print('json_payload',json_payload)
            ENDPOINT = 'user_management/login/'
            login_response = call_post_method_for_without_token(BASEURL,ENDPOINT,json_payload)
            print('login_response',login_response)
            if login_response.status_code == 200:
                login_tokes = login_response.json()
                request.session['user_token']=login_tokes['access']
                return redirect('/base_dashboard')
            else:
                login_tokes = login_response.json()
                login_error='Invalid Username and Password'
                context={"login_error":login_error}
                return render(request, 'login.html',context)
          
        return render(request, 'login.html')
    except Exception as error:
        return HttpResponse(f'<h1>{error}</h1>')

def main_dashboard(request):
    return render(request, 'v1/main_dashboard.html')
def compliance_dashboard(request):
    return render(request, 'v1/compliance_dashboard.html')
def campaign_dashboard(request):
    return render(request, 'v1/campaign_dashboard.html')
def delegate_dashboard(request):
    return render(request, 'v1/delegate_dashboard.html')
def advertising_dashboard(request):
    return render(request, 'v1/advertising_dashboard.html')
def board_evaluation_dashboard(request):
    return render(request, 'v1/board_evaluation_dashboard.html')
