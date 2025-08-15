from django import forms
from .models import *
from django.forms import BaseFormSet,DateInput, DateTimeInput, TimeInput, CheckboxInput, Textarea, TextInput
# from mainapp.forms import GenericModelForm

from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator, MaxValueValidator


class PolicyForm(forms.Form):
	title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	content = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	effective_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	expiry_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))


class BreachForm(forms.Form):
	reported_by = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	date_reported = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	policy = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		reported_by_list = kwargs.pop('reported_by_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_reported_by = initial_data.get('reported_by', '')
		policy_list = kwargs.pop('policy_choice', [])
		selected_policy = initial_data.get('policy', '')
		super().__init__(*args, **kwargs)
		self.fields['reported_by'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in reported_by_list ]
		self.fields['policy'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('title', '')) for record in policy_list]
		if selected_reported_by:
			self.fields['reported_by'].initial = selected_reported_by
		if selected_policy:
			self.fields['policy'].initial = selected_policy



class StaffPolicyAcknowledgmentForm(forms.Form):
	staff = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	policy = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	acknowledged_on = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		staff_list = kwargs.pop('staff_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_staff = initial_data.get('staff', '')
		policy_list = kwargs.pop('policy_choice', [])
		selected_policy = initial_data.get('policy', '')
		super().__init__(*args, **kwargs)
		self.fields['staff'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in staff_list ]
		self.fields['policy'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('title', '')) for record in policy_list]
		if selected_staff:
			self.fields['staff'].initial = selected_staff
		if selected_policy:
			self.fields['policy'].initial = selected_policy



class IncidentForm(forms.Form):
	title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	date_occurred = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	related_breach = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		related_breach_list = kwargs.pop('related_breach_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_related_breach = initial_data.get('related_breach', '')
		super().__init__(*args, **kwargs)
		self.fields['related_breach'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('description', '')) for record in related_breach_list]
		if selected_related_breach:
			self.fields['related_breach'].initial = selected_related_breach



class CorrectiveActionForm(forms.Form):
	incident = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	action_description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	due_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	completed = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
		incident_list = kwargs.pop('incident_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_incident = initial_data.get('incident', '')
		super().__init__(*args, **kwargs)
		self.fields['incident'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('title', '')) for record in incident_list]
		if selected_incident:
			self.fields['incident'].initial = selected_incident



class AuditEvidenceForm(forms.Form):
	name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	submitted_on = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))


class ComplianceCalendarEventForm(forms.Form):
	event_name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	due_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	status = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))


class RiskControlMatrixForm(forms.Form):
	risk = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	control = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	owner = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		owner_list = kwargs.pop('owner_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_owner = initial_data.get('owner', '')
		super().__init__(*args, **kwargs)
		self.fields['owner'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in owner_list ]
		if selected_owner:
			self.fields['owner'].initial = selected_owner



class ComplianceReturnForm(forms.Form):
	name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	period_start = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	period_end = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	data_source = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	submitted = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))


class WatchlistCheckForm(forms.Form):
	individual_or_entity = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	check_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	result = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
