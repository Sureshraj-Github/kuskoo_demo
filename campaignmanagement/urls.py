from django.urls import path,include
from .views import *
urlpatterns = [
    
	path("campaign/", campaign, name="campaign"),
	path("campaign_edit/<pk>/", campaign_edit, name="campaign_edit"),
	path("campaign_delete/<pk>/", campaign_delete, name="campaign_delete"),
	path("campaignchannel/", campaignchannel, name="campaignchannel"),
	path("campaignchannel_edit/<pk>/", campaignchannel_edit, name="campaignchannel_edit"),
	path("campaignchannel_delete/<pk>/", campaignchannel_delete, name="campaignchannel_delete"),
	path("event/", event, name="event"),
	path("event_edit/<pk>/", event_edit, name="event_edit"),
	path("event_delete/<pk>/", event_delete, name="event_delete"),
	path("impactmetric/", impactmetric, name="impactmetric"),
	path("impactmetric_edit/<pk>/", impactmetric_edit, name="impactmetric_edit"),
	path("impactmetric_delete/<pk>/", impactmetric_delete, name="impactmetric_delete"),
	path("mediamonitor/", mediamonitor, name="mediamonitor"),
	path("mediamonitor_edit/<pk>/", mediamonitor_edit, name="mediamonitor_edit"),
	path("mediamonitor_delete/<pk>/", mediamonitor_delete, name="mediamonitor_delete"),
	path("petition/", petition, name="petition"),
	path("petition_edit/<pk>/", petition_edit, name="petition_edit"),
	path("petition_delete/<pk>/", petition_delete, name="petition_delete"),
	path("stakeholder/", stakeholder, name="stakeholder"),
	path("stakeholder_edit/<pk>/", stakeholder_edit, name="stakeholder_edit"),
	path("stakeholder_delete/<pk>/", stakeholder_delete, name="stakeholder_delete"),
	path("issuebrief/", issuebrief, name="issuebrief"),
	path("issuebrief_edit/<pk>/", issuebrief_edit, name="issuebrief_edit"),
	path("issuebrief_delete/<pk>/", issuebrief_delete, name="issuebrief_delete"),
]