from django import forms
from .models import *
from django.forms import BaseFormSet,DateInput, DateTimeInput, TimeInput, CheckboxInput, Textarea, TextInput
# from mainapp.forms import GenericModelForm

from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator, MaxValueValidator


class CampaignForm(forms.Form):
	name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	objective = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	budget = forms.DecimalField(max_digits=12, decimal_places=2,required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
	start_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	end_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))


class CampaignChannelForm(forms.Form):
	campaign = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	channel_type = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	content_calendar = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		campaign_list = kwargs.pop('campaign_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_campaign = initial_data.get('campaign', '')
		super().__init__(*args, **kwargs)
		self.fields['campaign'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in campaign_list]
		if selected_campaign:
			self.fields['campaign'].initial = selected_campaign



class EventForm(forms.Form):
	campaign = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	attendees = forms.ChoiceField(required=False, widget=forms.SelectMultiple(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		campaign_list = kwargs.pop('campaign_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_campaign = initial_data.get('campaign', '')
		attendees_list = kwargs.pop('attendees_choice', [])
		selected_attendees = initial_data.get('attendees', '')
		super().__init__(*args, **kwargs)
		self.fields['campaign'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in campaign_list]
		self.fields['attendees'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in attendees_list ]
		if selected_campaign:
			self.fields['campaign'].initial = selected_campaign
		if selected_attendees:
			self.fields['attendees'].initial = selected_attendees



class ImpactMetricForm(forms.Form):
	campaign = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	reach = forms.IntegerField(validators=[MinValueValidator(0)],required=False,widget=forms.NumberInput(attrs={"class": "form-control"}))
	engagement = forms.IntegerField(validators=[MinValueValidator(0)],required=False,widget=forms.NumberInput(attrs={"class": "form-control"}))
	cost_per_outcome = forms.DecimalField(max_digits=10, decimal_places=2,required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		campaign_list = kwargs.pop('campaign_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_campaign = initial_data.get('campaign', '')
		super().__init__(*args, **kwargs)
		self.fields['campaign'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('name', '')) for record in campaign_list]
		if selected_campaign:
			self.fields['campaign'].initial = selected_campaign



class MediaMonitorForm(forms.Form):
	media_source = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	sentiment = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	response_needed = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))


class PetitionForm(forms.Form):
	title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	total_signatures = forms.IntegerField(validators=[MinValueValidator(0)],required=False,widget=forms.NumberInput(attrs={"class": "form-control"}))


class StakeholderForm(forms.Form):
	name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	type = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	influence_score = forms.IntegerField(validators=[MinValueValidator(0)],required=False,widget=forms.NumberInput(attrs={"class": "form-control"}))
	contact_info = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))


class IssueBriefForm(forms.Form):
	title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	content = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	approved = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	publication_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
