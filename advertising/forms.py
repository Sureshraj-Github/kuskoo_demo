from django import forms
from .models import *
from django.forms import BaseFormSet,DateInput, DateTimeInput, TimeInput, CheckboxInput, Textarea, TextInput
# from mainapp.forms import GenericModelForm

from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator, MaxValueValidator


class SocialPostForm(forms.Form):
	content = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	scheduled_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	platform = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	utm_code = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))


class ComplianceBannerForm(forms.Form):
	page = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	banner_text = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	consent_required = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
	accessibility_passed = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))


class ContentItemForm(forms.Form):
	title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	body = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	language = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	scheduled_publish = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={"type": "date","class": "form-control"}))
	published = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))


class SubscriptionForm(forms.Form):
	email = forms.EmailField(required=False, widget=forms.TextInput(attrs={"type": "email","class": "form-control"}))
	subscribed_on = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
	unsubscribed_on = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))


class MediaAssetForm(forms.Form):
	file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	asset_type = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	rights_expiry = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))


class AdBookingForm(forms.Form):
	advertiser_name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	inventory_type = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	rate = forms.DecimalField(max_digits=10, decimal_places=2,required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
	insertion_order = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))
	proof_of_play = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],required=False,widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}))


class NewsletterForm(forms.Form):
	subject = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	content = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control"}))
	sent_on = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))


class WebAnalyticsForm(forms.Form):
	page_url = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
	traffic = forms.IntegerField(validators=[MinValueValidator(0)],required=False,widget=forms.NumberInput(attrs={"class": "form-control"}))
	conversions = forms.IntegerField(validators=[MinValueValidator(0)],required=False,widget=forms.NumberInput(attrs={"class": "form-control"}))
	date = forms.DateField(input_formats=['%Y-%m-%d'],required=False, widget=forms.DateInput(attrs={"type": "date","class": "form-control"}))
