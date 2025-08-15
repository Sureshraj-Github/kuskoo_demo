from django.urls import path,include
from .views import *
urlpatterns = [
    
	path("electionevent/", electionevent, name="electionevent"),
	path("electionevent_edit/<pk>/", electionevent_edit, name="electionevent_edit"),
	path("electionevent_delete/<pk>/", electionevent_delete, name="electionevent_delete"),
	path("ballot/", ballot, name="ballot"),
	path("ballot_edit/<pk>/", ballot_edit, name="ballot_edit"),
	path("ballot_delete/<pk>/", ballot_delete, name="ballot_delete"),
	path("electionaudit/", electionaudit, name="electionaudit"),
	path("electionaudit_edit/<pk>/", electionaudit_edit, name="electionaudit_edit"),
	path("electionaudit_delete/<pk>/", electionaudit_delete, name="electionaudit_delete"),
	path("nomination/", nomination, name="nomination"),
	path("nomination_edit/<pk>/", nomination_edit, name="nomination_edit"),
	path("nomination_delete/<pk>/", nomination_delete, name="nomination_delete"),
	path("votinglog/", votinglog, name="votinglog"),
	path("votinglog_edit/<pk>/", votinglog_edit, name="votinglog_edit"),
	path("votinglog_delete/<pk>/", votinglog_delete, name="votinglog_delete"),
	path("votingresult/", votingresult, name="votingresult"),
	path("votingresult_edit/<pk>/", votingresult_edit, name="votingresult_edit"),
	path("votingresult_delete/<pk>/", votingresult_delete, name="votingresult_delete"),
]