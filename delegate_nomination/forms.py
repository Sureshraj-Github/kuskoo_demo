from django import forms
from .models import *
from django.forms import BaseFormSet,DateInput, DateTimeInput, TimeInput, CheckboxInput, Textarea, TextInput
# from mainapp.forms import GenericModelForm

from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator, MaxValueValidator


class ElectionEventForm(forms.Form):
	title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	start_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	end_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	election_type = forms.ChoiceField(choices=[('General', 'General'), ('Special', 'Special')], required=False,widget=forms.Select(attrs={"class": "form-control"}))
	eligibility_criteria = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))


class BallotForm(forms.Form):
	election_event = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	ballot_type = forms.ChoiceField(choices=[('Secret', 'Secret'), ('Weighted', 'Weighted')], required=False,widget=forms.Select(attrs={"class": "form-control"}))
	position = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	voting_start = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	voting_end = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		election_event_list = kwargs.pop('election_event_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_election_event = initial_data.get('election_event', '')
		super().__init__(*args, **kwargs)
		self.fields['election_event'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('title', '')) for record in election_event_list]
		if selected_election_event:
			self.fields['election_event'].initial = selected_election_event



class ElectionAuditForm(forms.Form):
	election_event = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	audit_report = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	data_retention_period = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	audit_date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	def __init__(self, *args, **kwargs):
		election_event_list = kwargs.pop('election_event_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_election_event = initial_data.get('election_event', '')
		super().__init__(*args, **kwargs)
		self.fields['election_event'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('title', '')) for record in election_event_list]
		if selected_election_event:
			self.fields['election_event'].initial = selected_election_event



class NominationForm(forms.Form):
	election_event = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	nominee = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	proposer = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	seconder = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	validated = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	status = forms.ChoiceField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], required=False,widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		election_event_list = kwargs.pop('election_event_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_election_event = initial_data.get('election_event', '')
		nominee_list = kwargs.pop('nominee_choice', [])
		selected_nominee = initial_data.get('nominee', '')
		proposer_list = kwargs.pop('proposer_choice', [])
		selected_proposer = initial_data.get('proposer', '')
		seconder_list = kwargs.pop('seconder_choice', [])
		selected_seconder = initial_data.get('seconder', '')
		super().__init__(*args, **kwargs)
		self.fields['election_event'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('title', '')) for record in election_event_list]
		self.fields['nominee'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in nominee_list ]
		self.fields['proposer'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in proposer_list ]
		self.fields['seconder'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in seconder_list ]
		if selected_election_event:
			self.fields['election_event'].initial = selected_election_event
		if selected_nominee:
			self.fields['nominee'].initial = selected_nominee
		if selected_proposer:
			self.fields['proposer'].initial = selected_proposer
		if selected_seconder:
			self.fields['seconder'].initial = selected_seconder



class VotingLogForm(forms.Form):
	voter = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	ballot = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	vote_choice = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	timestamp = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	tamper_evident = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	def __init__(self, *args, **kwargs):
		voter_list = kwargs.pop('voter_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_voter = initial_data.get('voter', '')
		ballot_list = kwargs.pop('ballot_choice', [])
		selected_ballot = initial_data.get('ballot', '')
		super().__init__(*args, **kwargs)
		self.fields['voter'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in voter_list ]
		self.fields['ballot'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('ballot_type', '')) for record in ballot_list]
		if selected_voter:
			self.fields['voter'].initial = selected_voter
		if selected_ballot:
			self.fields['ballot'].initial = selected_ballot



class VotingResultForm(forms.Form):
	ballot = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	nominee = forms.ChoiceField(required=False, widget=forms.Select(attrs={"class": "form-control"}))
	votes_received = forms.IntegerField(validators=[MinValueValidator(0)],required=False,widget=forms.NumberInput(attrs={"class": "form-control"}))
	result_status = forms.ChoiceField(choices=[('Won', 'Won'), ('Lost', 'Lost')], required=False,widget=forms.Select(attrs={"class": "form-control"}))
	def __init__(self, *args, **kwargs):
		ballot_list = kwargs.pop('ballot_choice', [])
		initial_data = kwargs.get("initial", {})
		selected_ballot = initial_data.get('ballot', '')
		nominee_list = kwargs.pop('nominee_choice', [])
		selected_nominee = initial_data.get('nominee', '')
		super().__init__(*args, **kwargs)
		self.fields['ballot'].choices = [('', '---select---')] + [(record.get('id', ''), record.get('ballot_type', '')) for record in ballot_list]
		self.fields['nominee'].choices = [('', '---select---')] + [(item.get('id', ''), item.get('first_name', '')) for item in nominee_list ]
		if selected_ballot:
			self.fields['ballot'].initial = selected_ballot
		if selected_nominee:
			self.fields['nominee'].initial = selected_nominee

