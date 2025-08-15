from django.urls import path,include
from .views import *
urlpatterns = [
    
	path("boardmeeting/", boardmeeting, name="boardmeeting"),
	path("boardmeeting_edit/<pk>/", boardmeeting_edit, name="boardmeeting_edit"),
	path("boardmeeting_delete/<pk>/", boardmeeting_delete, name="boardmeeting_delete"),
	path("actionitem/", actionitem, name="actionitem"),
	path("actionitem_edit/<pk>/", actionitem_edit, name="actionitem_edit"),
	path("actionitem_delete/<pk>/", actionitem_delete, name="actionitem_delete"),
	path("decisionlog/", decisionlog, name="decisionlog"),
	path("decisionlog_edit/<pk>/", decisionlog_edit, name="decisionlog_edit"),
	path("decisionlog_delete/<pk>/", decisionlog_delete, name="decisionlog_delete"),
	path("conflictofinterest/", conflictofinterest, name="conflictofinterest"),
	path("conflictofinterest_edit/<pk>/", conflictofinterest_edit, name="conflictofinterest_edit"),
	path("conflictofinterest_delete/<pk>/", conflictofinterest_delete, name="conflictofinterest_delete"),
	path("boardkpi/", boardkpi, name="boardkpi"),
	path("boardkpi_edit/<pk>/", boardkpi_edit, name="boardkpi_edit"),
	path("boardkpi_delete/<pk>/", boardkpi_delete, name="boardkpi_delete"),
	path("boardevaluation/", boardevaluation, name="boardevaluation"),
	path("boardevaluation_edit/<pk>/", boardevaluation_edit, name="boardevaluation_edit"),
	path("boardevaluation_delete/<pk>/", boardevaluation_delete, name="boardevaluation_delete"),
]