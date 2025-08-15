from django.urls import path

from .views import *

urlpatterns = [
    path("",login, name="login"),
    path("base_dashboard/",base_dashboard, name="base_dashboard"),
    path("main_dashboard/",main_dashboard, name="main_dashboard"),
    path("compliance_dashboard/",compliance_dashboard, name="compliance_dashboard"),
    path("campaign_dashboard/",campaign_dashboard, name="campaign_dashboard"),
    path("delegate_dashboard/",delegate_dashboard, name="delegate_dashboard"),
    path("advertising_dashboard/",advertising_dashboard, name="advertising_dashboard"),
    path("board_evaluation_dashboard/",board_evaluation_dashboard, name="board_evaluation_dashboard"),


]