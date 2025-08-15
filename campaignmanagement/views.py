from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.forms import modelformset_factory
from mainapp.views import *
from django.template.loader import render_to_string

APP_NAME = __name__.split('.')[0]

BASEURL = settings.BASEURL


# create and view table function
@custom_login_required
def campaign(request):
    try:
        token = request.session['user_token']


        form=CampaignForm()
        endpoint = 'campaignmanagement/campaign/'
        if request.method=="POST":
            form=CampaignForm(request.POST,files = request.FILES,)
            if form.is_valid():
                Output = form.cleaned_data
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField) or isinstance(field, forms.TimeField):
                        if Output[field_name]:
                            del Output[field_name]
                            Output[field_name] = request.POST.get(field_name)
                json_data=json.dumps(Output)
                response = call_post_with_method(BASEURL,endpoint,json_data,token)
                if response.status_code in [200,201]:
                    print("error",response)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'Data Successfully Saved', extra_tags="success")
                    return redirect('campaign')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('campaign_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'campaign.html', {
                    'form': form,
                    'records': records,
                })
            else:
                messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

        except Exception as e:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        context={
            'form':form,
            'records':[]
        }
        return render(request,'campaign.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def campaign_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        campaign = call_get_method(BASEURL, f'campaignmanagement/campaign/{pk}/',token)
        
        if campaign.status_code in [200,201]:
            campaign_data = campaign.json()
        else:
            print('error------',campaign)
            messages.error(request, 'Failed to retrieve data for campaign. Please check your connection and try again.', extra_tags='warning')
            return redirect('campaign')

        if request.method=="POST":
            form=CampaignForm(request.POST,files = request.FILES, initial=campaign_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'campaignmanagement/campaign/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'campaign successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('campaign') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('campaign_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = CampaignForm(initial=campaign_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('campaign_edit.html', {'form': form, 'campaign_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'campaign_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def campaign_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'campaignmanagement/campaign/{pk}/'
        campaign = call_delete_method(BASEURL, end_point,token)
        if campaign.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for campaign. Please try again.', extra_tags='warning')
            return redirect('campaign')
        else:
            messages.success(request, 'Successfully deleted data for campaign', extra_tags='success')
            return redirect('campaign')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def campaignchannel(request):
    try:
        token = request.session['user_token']


        campaign_response = call_get_method(BASEURL, 'campaignmanagement/campaign/', token)
        if campaign_response.status_code in [200,201]:
            campaign_records = campaign_response.json()
        else:
            campaign_records = []
    

        form=CampaignChannelForm(campaign_choice=campaign_records)
        endpoint = 'campaignmanagement/campaignchannel/'
        if request.method=="POST":
            form=CampaignChannelForm(request.POST,files = request.FILES,campaign_choice=campaign_records)
            if form.is_valid():
                Output = form.cleaned_data
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField) or isinstance(field, forms.TimeField):
                        if Output[field_name]:
                            del Output[field_name]
                            Output[field_name] = request.POST.get(field_name)
                json_data=json.dumps(Output)
                response = call_post_with_method(BASEURL,endpoint,json_data,token)
                if response.status_code in [200,201]:
                    print("error",response)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'Data Successfully Saved', extra_tags="success")
                    return redirect('campaignchannel')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('campaignchannel_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'campaignchannel.html', {
                    'form': form,
                    'records': records,
                })
            else:
                messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

        except Exception as e:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        context={
            'form':form,
            'records':[]
        }
        return render(request,'campaignchannel.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def campaignchannel_edit(request,pk):
    try:

        token = request.session['user_token']


        campaign_response = call_get_method(BASEURL, 'campaignmanagement/campaign/', token)
        if campaign_response.status_code in [200,201]:
            campaign_records = campaign_response.json()
        else:
            campaign_records = []
    


        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        campaignchannel = call_get_method(BASEURL, f'campaignmanagement/campaignchannel/{pk}/',token)
        
        if campaignchannel.status_code in [200,201]:
            campaignchannel_data = campaignchannel.json()
        else:
            print('error------',campaignchannel)
            messages.error(request, 'Failed to retrieve data for campaignchannel. Please check your connection and try again.', extra_tags='warning')
            return redirect('campaignchannel')

        if request.method=="POST":
            form=CampaignChannelForm(request.POST,files = request.FILES, initial=campaignchannel_data,campaign_choice=campaign_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'campaignmanagement/campaignchannel/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'campaignchannel successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('campaignchannel') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('campaignchannel_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = CampaignChannelForm(initial=campaignchannel_data,campaign_choice=campaign_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('campaignchannel_edit.html', {'form': form, 'campaignchannel_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'campaignchannel_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def campaignchannel_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'campaignmanagement/campaignchannel/{pk}/'
        campaignchannel = call_delete_method(BASEURL, end_point,token)
        if campaignchannel.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for campaignchannel. Please try again.', extra_tags='warning')
            return redirect('campaignchannel')
        else:
            messages.success(request, 'Successfully deleted data for campaignchannel', extra_tags='success')
            return redirect('campaignchannel')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def event(request):
    try:
        token = request.session['user_token']


        campaign_response = call_get_method(BASEURL, 'campaignmanagement/campaign/', token)
        if campaign_response.status_code in [200,201]:
            campaign_records = campaign_response.json()
        else:
            campaign_records = []
    
   
        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            attendees_records = user_response.json()
        else:
            attendees_records = []


        form=EventForm(campaign_choice=campaign_records,attendees_choice=attendees_records)
        endpoint = 'campaignmanagement/event/'
        if request.method=="POST":
            form=EventForm(request.POST,files = request.FILES,campaign_choice=campaign_records,attendees_choice=attendees_records)
            if form.is_valid():
                Output = form.cleaned_data
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField) or isinstance(field, forms.TimeField):
                        if Output[field_name]:
                            del Output[field_name]
                            Output[field_name] = request.POST.get(field_name)
                json_data=json.dumps(Output)
                response = call_post_with_method(BASEURL,endpoint,json_data,token)
                if response.status_code in [200,201]:
                    print("error",response)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'Data Successfully Saved', extra_tags="success")
                    return redirect('event')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('event_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'event.html', {
                    'form': form,
                    'records': records,
                })
            else:
                messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

        except Exception as e:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        context={
            'form':form,
            'records':[]
        }
        return render(request,'event.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def event_edit(request,pk):
    try:

        token = request.session['user_token']


        campaign_response = call_get_method(BASEURL, 'campaignmanagement/campaign/', token)
        if campaign_response.status_code in [200,201]:
            campaign_records = campaign_response.json()
        else:
            campaign_records = []
    
   
        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            attendees_records = user_response.json()
        else:
            attendees_records = []



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        event = call_get_method(BASEURL, f'campaignmanagement/event/{pk}/',token)
        
        if event.status_code in [200,201]:
            event_data = event.json()
        else:
            print('error------',event)
            messages.error(request, 'Failed to retrieve data for event. Please check your connection and try again.', extra_tags='warning')
            return redirect('event')

        if request.method=="POST":
            form=EventForm(request.POST,files = request.FILES, initial=event_data,campaign_choice=campaign_records,attendees_choice=attendees_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'campaignmanagement/event/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'event successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('event') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('event_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = EventForm(initial=event_data,campaign_choice=campaign_records,attendees_choice=attendees_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('event_edit.html', {'form': form, 'event_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'event_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def event_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'campaignmanagement/event/{pk}/'
        event = call_delete_method(BASEURL, end_point,token)
        if event.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for event. Please try again.', extra_tags='warning')
            return redirect('event')
        else:
            messages.success(request, 'Successfully deleted data for event', extra_tags='success')
            return redirect('event')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def impactmetric(request):
    try:
        token = request.session['user_token']


        campaign_response = call_get_method(BASEURL, 'campaignmanagement/campaign/', token)
        if campaign_response.status_code in [200,201]:
            campaign_records = campaign_response.json()
        else:
            campaign_records = []
    

        form=ImpactMetricForm(campaign_choice=campaign_records)
        endpoint = 'campaignmanagement/impactmetric/'
        if request.method=="POST":
            form=ImpactMetricForm(request.POST,files = request.FILES,campaign_choice=campaign_records)
            if form.is_valid():
                Output = form.cleaned_data
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField) or isinstance(field, forms.TimeField):
                        if Output[field_name]:
                            del Output[field_name]
                            Output[field_name] = request.POST.get(field_name)
                json_data=json.dumps(Output)
                response = call_post_with_method(BASEURL,endpoint,json_data,token)
                if response.status_code in [200,201]:
                    print("error",response)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'Data Successfully Saved', extra_tags="success")
                    return redirect('impactmetric')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('impactmetric_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'impactmetric.html', {
                    'form': form,
                    'records': records,
                })
            else:
                messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

        except Exception as e:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        context={
            'form':form,
            'records':[]
        }
        return render(request,'impactmetric.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def impactmetric_edit(request,pk):
    try:

        token = request.session['user_token']


        campaign_response = call_get_method(BASEURL, 'campaignmanagement/campaign/', token)
        if campaign_response.status_code in [200,201]:
            campaign_records = campaign_response.json()
        else:
            campaign_records = []
    


        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        impactmetric = call_get_method(BASEURL, f'campaignmanagement/impactmetric/{pk}/',token)
        
        if impactmetric.status_code in [200,201]:
            impactmetric_data = impactmetric.json()
        else:
            print('error------',impactmetric)
            messages.error(request, 'Failed to retrieve data for impactmetric. Please check your connection and try again.', extra_tags='warning')
            return redirect('impactmetric')

        if request.method=="POST":
            form=ImpactMetricForm(request.POST,files = request.FILES, initial=impactmetric_data,campaign_choice=campaign_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'campaignmanagement/impactmetric/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'impactmetric successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('impactmetric') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('impactmetric_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = ImpactMetricForm(initial=impactmetric_data,campaign_choice=campaign_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('impactmetric_edit.html', {'form': form, 'impactmetric_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'impactmetric_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def impactmetric_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'campaignmanagement/impactmetric/{pk}/'
        impactmetric = call_delete_method(BASEURL, end_point,token)
        if impactmetric.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for impactmetric. Please try again.', extra_tags='warning')
            return redirect('impactmetric')
        else:
            messages.success(request, 'Successfully deleted data for impactmetric', extra_tags='success')
            return redirect('impactmetric')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def mediamonitor(request):
    try:
        token = request.session['user_token']


        form=MediaMonitorForm()
        endpoint = 'campaignmanagement/mediamonitor/'
        if request.method=="POST":
            form=MediaMonitorForm(request.POST,files = request.FILES,)
            if form.is_valid():
                Output = form.cleaned_data
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField) or isinstance(field, forms.TimeField):
                        if Output[field_name]:
                            del Output[field_name]
                            Output[field_name] = request.POST.get(field_name)
                json_data=json.dumps(Output)
                response = call_post_with_method(BASEURL,endpoint,json_data,token)
                if response.status_code in [200,201]:
                    print("error",response)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'Data Successfully Saved', extra_tags="success")
                    return redirect('mediamonitor')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('mediamonitor_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'mediamonitor.html', {
                    'form': form,
                    'records': records,
                })
            else:
                messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

        except Exception as e:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        context={
            'form':form,
            'records':[]
        }
        return render(request,'mediamonitor.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def mediamonitor_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        mediamonitor = call_get_method(BASEURL, f'campaignmanagement/mediamonitor/{pk}/',token)
        
        if mediamonitor.status_code in [200,201]:
            mediamonitor_data = mediamonitor.json()
        else:
            print('error------',mediamonitor)
            messages.error(request, 'Failed to retrieve data for mediamonitor. Please check your connection and try again.', extra_tags='warning')
            return redirect('mediamonitor')

        if request.method=="POST":
            form=MediaMonitorForm(request.POST,files = request.FILES, initial=mediamonitor_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'campaignmanagement/mediamonitor/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'mediamonitor successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('mediamonitor') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('mediamonitor_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = MediaMonitorForm(initial=mediamonitor_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('mediamonitor_edit.html', {'form': form, 'mediamonitor_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'mediamonitor_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def mediamonitor_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'campaignmanagement/mediamonitor/{pk}/'
        mediamonitor = call_delete_method(BASEURL, end_point,token)
        if mediamonitor.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for mediamonitor. Please try again.', extra_tags='warning')
            return redirect('mediamonitor')
        else:
            messages.success(request, 'Successfully deleted data for mediamonitor', extra_tags='success')
            return redirect('mediamonitor')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def petition(request):
    try:
        token = request.session['user_token']


        form=PetitionForm()
        endpoint = 'campaignmanagement/petition/'
        if request.method=="POST":
            form=PetitionForm(request.POST,files = request.FILES,)
            if form.is_valid():
                Output = form.cleaned_data
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField) or isinstance(field, forms.TimeField):
                        if Output[field_name]:
                            del Output[field_name]
                            Output[field_name] = request.POST.get(field_name)
                json_data=json.dumps(Output)
                response = call_post_with_method(BASEURL,endpoint,json_data,token)
                if response.status_code in [200,201]:
                    print("error",response)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'Data Successfully Saved', extra_tags="success")
                    return redirect('petition')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('petition_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'petition.html', {
                    'form': form,
                    'records': records,
                })
            else:
                messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

        except Exception as e:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        context={
            'form':form,
            'records':[]
        }
        return render(request,'petition.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def petition_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        petition = call_get_method(BASEURL, f'campaignmanagement/petition/{pk}/',token)
        
        if petition.status_code in [200,201]:
            petition_data = petition.json()
        else:
            print('error------',petition)
            messages.error(request, 'Failed to retrieve data for petition. Please check your connection and try again.', extra_tags='warning')
            return redirect('petition')

        if request.method=="POST":
            form=PetitionForm(request.POST,files = request.FILES, initial=petition_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'campaignmanagement/petition/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'petition successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('petition') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('petition_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = PetitionForm(initial=petition_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('petition_edit.html', {'form': form, 'petition_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'petition_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def petition_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'campaignmanagement/petition/{pk}/'
        petition = call_delete_method(BASEURL, end_point,token)
        if petition.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for petition. Please try again.', extra_tags='warning')
            return redirect('petition')
        else:
            messages.success(request, 'Successfully deleted data for petition', extra_tags='success')
            return redirect('petition')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def stakeholder(request):
    try:
        token = request.session['user_token']


        form=StakeholderForm()
        endpoint = 'campaignmanagement/stakeholder/'
        if request.method=="POST":
            form=StakeholderForm(request.POST,files = request.FILES,)
            if form.is_valid():
                Output = form.cleaned_data
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField) or isinstance(field, forms.TimeField):
                        if Output[field_name]:
                            del Output[field_name]
                            Output[field_name] = request.POST.get(field_name)
                json_data=json.dumps(Output)
                response = call_post_with_method(BASEURL,endpoint,json_data,token)
                if response.status_code in [200,201]:
                    print("error",response)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'Data Successfully Saved', extra_tags="success")
                    return redirect('stakeholder')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('stakeholder_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'stakeholder.html', {
                    'form': form,
                    'records': records,
                })
            else:
                messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

        except Exception as e:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        context={
            'form':form,
            'records':[]
        }
        return render(request,'stakeholder.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def stakeholder_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        stakeholder = call_get_method(BASEURL, f'campaignmanagement/stakeholder/{pk}/',token)
        
        if stakeholder.status_code in [200,201]:
            stakeholder_data = stakeholder.json()
        else:
            print('error------',stakeholder)
            messages.error(request, 'Failed to retrieve data for stakeholder. Please check your connection and try again.', extra_tags='warning')
            return redirect('stakeholder')

        if request.method=="POST":
            form=StakeholderForm(request.POST,files = request.FILES, initial=stakeholder_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'campaignmanagement/stakeholder/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'stakeholder successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('stakeholder') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('stakeholder_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = StakeholderForm(initial=stakeholder_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('stakeholder_edit.html', {'form': form, 'stakeholder_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'stakeholder_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def stakeholder_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'campaignmanagement/stakeholder/{pk}/'
        stakeholder = call_delete_method(BASEURL, end_point,token)
        if stakeholder.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for stakeholder. Please try again.', extra_tags='warning')
            return redirect('stakeholder')
        else:
            messages.success(request, 'Successfully deleted data for stakeholder', extra_tags='success')
            return redirect('stakeholder')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def issuebrief(request):
    try:
        token = request.session['user_token']


        form=IssueBriefForm()
        endpoint = 'campaignmanagement/issuebrief/'
        if request.method=="POST":
            form=IssueBriefForm(request.POST,files = request.FILES,)
            if form.is_valid():
                Output = form.cleaned_data
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, forms.DateField) or isinstance(field, forms.DateTimeField) or isinstance(field, forms.DecimalField) or isinstance(field, forms.TimeField):
                        if Output[field_name]:
                            del Output[field_name]
                            Output[field_name] = request.POST.get(field_name)
                json_data=json.dumps(Output)
                response = call_post_with_method(BASEURL,endpoint,json_data,token)
                if response.status_code in [200,201]:
                    print("error",response)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'Data Successfully Saved', extra_tags="success")
                    return redirect('issuebrief')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('issuebrief_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'issuebrief.html', {
                    'form': form,
                    'records': records,
                })
            else:
                messages.error(request, f"Failed to fetch records. {records_response.json()}", extra_tags="warning")

        except Exception as e:
            print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        context={
            'form':form,
            'records':[]
        }
        return render(request,'issuebrief.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def issuebrief_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        issuebrief = call_get_method(BASEURL, f'campaignmanagement/issuebrief/{pk}/',token)
        
        if issuebrief.status_code in [200,201]:
            issuebrief_data = issuebrief.json()
        else:
            print('error------',issuebrief)
            messages.error(request, 'Failed to retrieve data for issuebrief. Please check your connection and try again.', extra_tags='warning')
            return redirect('issuebrief')

        if request.method=="POST":
            form=IssueBriefForm(request.POST,files = request.FILES, initial=issuebrief_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'campaignmanagement/issuebrief/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'issuebrief successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('issuebrief') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('issuebrief_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = IssueBriefForm(initial=issuebrief_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('issuebrief_edit.html', {'form': form, 'issuebrief_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'issuebrief_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def issuebrief_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'campaignmanagement/issuebrief/{pk}/'
        issuebrief = call_delete_method(BASEURL, end_point,token)
        if issuebrief.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for issuebrief. Please try again.', extra_tags='warning')
            return redirect('issuebrief')
        else:
            messages.success(request, 'Successfully deleted data for issuebrief', extra_tags='success')
            return redirect('issuebrief')

    except Exception as error:
        return render(request,'500.html',{'error':error})
