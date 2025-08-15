from django.urls import path,include
from .views import *
urlpatterns = [
    
	path("socialpost/", socialpost, name="socialpost"),
	path("socialpost_edit/<pk>/", socialpost_edit, name="socialpost_edit"),
	path("socialpost_delete/<pk>/", socialpost_delete, name="socialpost_delete"),
	path("compliancebanner/", compliancebanner, name="compliancebanner"),
	path("compliancebanner_edit/<pk>/", compliancebanner_edit, name="compliancebanner_edit"),
	path("compliancebanner_delete/<pk>/", compliancebanner_delete, name="compliancebanner_delete"),
	path("contentitem/", contentitem, name="contentitem"),
	path("contentitem_edit/<pk>/", contentitem_edit, name="contentitem_edit"),
	path("contentitem_delete/<pk>/", contentitem_delete, name="contentitem_delete"),
	path("subscription/", subscription, name="subscription"),
	path("subscription_edit/<pk>/", subscription_edit, name="subscription_edit"),
	path("subscription_delete/<pk>/", subscription_delete, name="subscription_delete"),
	path("mediaasset/", mediaasset, name="mediaasset"),
	path("mediaasset_edit/<pk>/", mediaasset_edit, name="mediaasset_edit"),
	path("mediaasset_delete/<pk>/", mediaasset_delete, name="mediaasset_delete"),
	path("adbooking/", adbooking, name="adbooking"),
	path("adbooking_edit/<pk>/", adbooking_edit, name="adbooking_edit"),
	path("adbooking_delete/<pk>/", adbooking_delete, name="adbooking_delete"),
	path("newsletter/", newsletter, name="newsletter"),
	path("newsletter_edit/<pk>/", newsletter_edit, name="newsletter_edit"),
	path("newsletter_delete/<pk>/", newsletter_delete, name="newsletter_delete"),
	path("webanalytics/", webanalytics, name="webanalytics"),
	path("webanalytics_edit/<pk>/", webanalytics_edit, name="webanalytics_edit"),
	path("webanalytics_delete/<pk>/", webanalytics_delete, name="webanalytics_delete"),
]