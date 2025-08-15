from django import forms
from .models import *
from django.forms import BaseFormSet,DateInput, DateTimeInput, TimeInput, CheckboxInput, Textarea, TextInput
# from mainapp.forms import GenericModelForm

from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator, MaxValueValidator


class BoardMeetingForm(forms.Form):
	title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	agenda = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	meeting_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	minutes = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	resolutions = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))


class ActionItemForm(forms.Form):
	board_meeting = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	owner = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	due_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	status = forms.ChoiceField(choices=[('Pending', 'Pending'), ('Completed', 'Completed')], required=False,widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		board_meeting_list = kwargs.pop('board_meeting_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_board_meeting = initial_data.get('board_meeting', '')
		owner_list = kwargs.pop('owner_choice', [])
		selected_owner = initial_data.get('owner', '')
		super().__init__(*args, **kwargs)
		self.fields['board_meeting'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('title', '')) for record in board_meeting_list]
		self.fields['owner'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in owner_list ]
		if selected_board_meeting:
			self.fields['board_meeting'].initial = selected_board_meeting
		if selected_owner:
			self.fields['owner'].initial = selected_owner



class DecisionLogForm(forms.Form):
	decision = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	date_made = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	board_meeting = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	decision_made_by = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		board_meeting_list = kwargs.pop('board_meeting_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_board_meeting = initial_data.get('board_meeting', '')
		decision_made_by_list = kwargs.pop('decision_made_by_choice', [])
		selected_decision_made_by = initial_data.get('decision_made_by', '')
		super().__init__(*args, **kwargs)
		self.fields['board_meeting'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('title', '')) for record in board_meeting_list]
		self.fields['decision_made_by'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in decision_made_by_list ]
		if selected_board_meeting:
			self.fields['board_meeting'].initial = selected_board_meeting
		if selected_decision_made_by:
			self.fields['decision_made_by'].initial = selected_decision_made_by



class ConflictOfInterestForm(forms.Form):
	board_member = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	declaration = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	gift_received = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	status = forms.ChoiceField(choices=[('Open', 'Open'), ('Resolved', 'Resolved')], required=False,widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		board_member_list = kwargs.pop('board_member_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_board_member = initial_data.get('board_member', '')
		super().__init__(*args, **kwargs)
		self.fields['board_member'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in board_member_list ]
		if selected_board_member:
			self.fields['board_member'].initial = selected_board_member



class BoardKPIForm(forms.Form):
	board_member = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	attendance_rate = forms.DecimalField(max_digits=5, decimal_places=2,required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
	resolution_closure_rate = forms.DecimalField(max_digits=5, decimal_places=2,required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
	policy_currency_rate = forms.DecimalField(max_digits=5, decimal_places=2,required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		board_member_list = kwargs.pop('board_member_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_board_member = initial_data.get('board_member', '')
		super().__init__(*args, **kwargs)
		self.fields['board_member'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in board_member_list ]
		if selected_board_member:
			self.fields['board_member'].initial = selected_board_member



class BoardEvaluationForm(forms.Form):
	board_member = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	evaluator = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	survey_type = forms.ChoiceField(choices=[('Self', 'Self'), ('Peer', 'Peer'), ('360', '360')], required=False,widget=forms.Select(attrs={"class": "form-control"}))
	score = forms.IntegerField(validators=[MinValueValidator(0)],required=False,widget=forms.NumberInput(attrs={"class": "form-control"}))
	comments = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	date_taken = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		board_member_list = kwargs.pop('board_member_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_board_member = initial_data.get('board_member', '')
		evaluator_list = kwargs.pop('evaluator_choice', [])
		selected_evaluator = initial_data.get('evaluator', '')
		super().__init__(*args, **kwargs)
		self.fields['board_member'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in board_member_list ]
		self.fields['evaluator'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in evaluator_list ]
		if selected_board_member:
			self.fields['board_member'].initial = selected_board_member
		if selected_evaluator:
			self.fields['evaluator'].initial = selected_evaluator

