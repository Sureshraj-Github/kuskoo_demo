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
def electionevent(request):
    try:
        token = request.session['user_token']


        form=ElectionEventForm()
        endpoint = 'delegate_nomination/electionevent/'
        if request.method=="POST":
            form=ElectionEventForm(request.POST,files = request.FILES,)
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
                    return redirect('electionevent')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('electionevent_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'electionevent.html', {
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
        return render(request,'electionevent.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def electionevent_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        electionevent = call_get_method(BASEURL, f'delegate_nomination/electionevent/{pk}/',token)
        
        if electionevent.status_code in [200,201]:
            electionevent_data = electionevent.json()
        else:
            print('error------',electionevent)
            messages.error(request, 'Failed to retrieve data for electionevent. Please check your connection and try again.', extra_tags='warning')
            return redirect('electionevent')

        if request.method=="POST":
            form=ElectionEventForm(request.POST,files = request.FILES, initial=electionevent_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'delegate_nomination/electionevent/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'electionevent successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('electionevent') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('electionevent_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = ElectionEventForm(initial=electionevent_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('electionevent_edit.html', {'form': form, 'electionevent_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'electionevent_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def electionevent_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'delegate_nomination/electionevent/{pk}/'
        electionevent = call_delete_method(BASEURL, end_point,token)
        if electionevent.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for electionevent. Please try again.', extra_tags='warning')
            return redirect('electionevent')
        else:
            messages.success(request, 'Successfully deleted data for electionevent', extra_tags='success')
            return redirect('electionevent')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def ballot(request):
    try:
        token = request.session['user_token']


        election_event_response = call_get_method(BASEURL, 'delegate_nomination/electionevent/', token)
        if election_event_response.status_code in [200,201]:
            election_event_records = election_event_response.json()
        else:
            election_event_records = []
    

        form=BallotForm(election_event_choice=election_event_records)
        endpoint = 'delegate_nomination/ballot/'
        if request.method=="POST":
            form=BallotForm(request.POST,files = request.FILES,election_event_choice=election_event_records)
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
                    return redirect('ballot')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('ballot_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'ballot.html', {
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
        return render(request,'ballot.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def ballot_edit(request,pk):
    try:

        token = request.session['user_token']


        election_event_response = call_get_method(BASEURL, 'delegate_nomination/electionevent/', token)
        if election_event_response.status_code in [200,201]:
            election_event_records = election_event_response.json()
        else:
            election_event_records = []
    


        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        ballot = call_get_method(BASEURL, f'delegate_nomination/ballot/{pk}/',token)
        
        if ballot.status_code in [200,201]:
            ballot_data = ballot.json()
        else:
            print('error------',ballot)
            messages.error(request, 'Failed to retrieve data for ballot. Please check your connection and try again.', extra_tags='warning')
            return redirect('ballot')

        if request.method=="POST":
            form=BallotForm(request.POST,files = request.FILES, initial=ballot_data,election_event_choice=election_event_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'delegate_nomination/ballot/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'ballot successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('ballot') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('ballot_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = BallotForm(initial=ballot_data,election_event_choice=election_event_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('ballot_edit.html', {'form': form, 'ballot_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'ballot_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def ballot_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'delegate_nomination/ballot/{pk}/'
        ballot = call_delete_method(BASEURL, end_point,token)
        if ballot.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for ballot. Please try again.', extra_tags='warning')
            return redirect('ballot')
        else:
            messages.success(request, 'Successfully deleted data for ballot', extra_tags='success')
            return redirect('ballot')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def electionaudit(request):
    try:
        token = request.session['user_token']


        election_event_response = call_get_method(BASEURL, 'delegate_nomination/electionevent/', token)
        if election_event_response.status_code in [200,201]:
            election_event_records = election_event_response.json()
        else:
            election_event_records = []
    

        form=ElectionAuditForm(election_event_choice=election_event_records)
        endpoint = 'delegate_nomination/electionaudit/'
        if request.method=="POST":
            form=ElectionAuditForm(request.POST,files = request.FILES,election_event_choice=election_event_records)
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
                    return redirect('electionaudit')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('electionaudit_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'electionaudit.html', {
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
        return render(request,'electionaudit.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def electionaudit_edit(request,pk):
    try:

        token = request.session['user_token']


        election_event_response = call_get_method(BASEURL, 'delegate_nomination/electionevent/', token)
        if election_event_response.status_code in [200,201]:
            election_event_records = election_event_response.json()
        else:
            election_event_records = []
    


        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        electionaudit = call_get_method(BASEURL, f'delegate_nomination/electionaudit/{pk}/',token)
        
        if electionaudit.status_code in [200,201]:
            electionaudit_data = electionaudit.json()
        else:
            print('error------',electionaudit)
            messages.error(request, 'Failed to retrieve data for electionaudit. Please check your connection and try again.', extra_tags='warning')
            return redirect('electionaudit')

        if request.method=="POST":
            form=ElectionAuditForm(request.POST,files = request.FILES, initial=electionaudit_data,election_event_choice=election_event_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'delegate_nomination/electionaudit/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'electionaudit successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('electionaudit') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('electionaudit_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = ElectionAuditForm(initial=electionaudit_data,election_event_choice=election_event_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('electionaudit_edit.html', {'form': form, 'electionaudit_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'electionaudit_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def electionaudit_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'delegate_nomination/electionaudit/{pk}/'
        electionaudit = call_delete_method(BASEURL, end_point,token)
        if electionaudit.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for electionaudit. Please try again.', extra_tags='warning')
            return redirect('electionaudit')
        else:
            messages.success(request, 'Successfully deleted data for electionaudit', extra_tags='success')
            return redirect('electionaudit')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def nomination(request):
    try:
        token = request.session['user_token']


        election_event_response = call_get_method(BASEURL, 'delegate_nomination/electionevent/', token)
        if election_event_response.status_code in [200,201]:
            election_event_records = election_event_response.json()
        else:
            election_event_records = []
    
   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            nominee_records = user_response.json()
        else:
            nominee_records = []

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            proposer_records = user_response.json()
        else:
            proposer_records = []

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            seconder_records = user_response.json()
        else:
            seconder_records = []


        form=NominationForm(election_event_choice=election_event_records,nominee_choice=nominee_records,proposer_choice=proposer_records,seconder_choice=seconder_records)
        endpoint = 'delegate_nomination/nomination/'
        if request.method=="POST":
            form=NominationForm(request.POST,files = request.FILES,election_event_choice=election_event_records,nominee_choice=nominee_records,proposer_choice=proposer_records,seconder_choice=seconder_records)
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
                    return redirect('nomination')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('nomination_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'nomination.html', {
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
        return render(request,'nomination.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def nomination_edit(request,pk):
    try:

        token = request.session['user_token']


        election_event_response = call_get_method(BASEURL, 'delegate_nomination/electionevent/', token)
        if election_event_response.status_code in [200,201]:
            election_event_records = election_event_response.json()
        else:
            election_event_records = []
    
   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            nominee_records = user_response.json()
        else:
            nominee_records = []

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            proposer_records = user_response.json()
        else:
            proposer_records = []

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            seconder_records = user_response.json()
        else:
            seconder_records = []



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        nomination = call_get_method(BASEURL, f'delegate_nomination/nomination/{pk}/',token)
        
        if nomination.status_code in [200,201]:
            nomination_data = nomination.json()
        else:
            print('error------',nomination)
            messages.error(request, 'Failed to retrieve data for nomination. Please check your connection and try again.', extra_tags='warning')
            return redirect('nomination')

        if request.method=="POST":
            form=NominationForm(request.POST,files = request.FILES, initial=nomination_data,election_event_choice=election_event_records,nominee_choice=nominee_records,proposer_choice=proposer_records,seconder_choice=seconder_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'delegate_nomination/nomination/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'nomination successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('nomination') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('nomination_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = NominationForm(initial=nomination_data,election_event_choice=election_event_records,nominee_choice=nominee_records,proposer_choice=proposer_records,seconder_choice=seconder_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('nomination_edit.html', {'form': form, 'nomination_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'nomination_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def nomination_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'delegate_nomination/nomination/{pk}/'
        nomination = call_delete_method(BASEURL, end_point,token)
        if nomination.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for nomination. Please try again.', extra_tags='warning')
            return redirect('nomination')
        else:
            messages.success(request, 'Successfully deleted data for nomination', extra_tags='success')
            return redirect('nomination')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def votinglog(request):
    try:
        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            voter_records = user_response.json()
        else:
            voter_records = []


        ballot_response = call_get_method(BASEURL, 'delegate_nomination/ballot/', token)
        if ballot_response.status_code in [200,201]:
            ballot_records = ballot_response.json()
        else:
            ballot_records = []
    

        form=VotingLogForm(voter_choice=voter_records,ballot_choice=ballot_records)
        endpoint = 'delegate_nomination/votinglog/'
        if request.method=="POST":
            form=VotingLogForm(request.POST,files = request.FILES,voter_choice=voter_records,ballot_choice=ballot_records)
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
                    return redirect('votinglog')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('votinglog_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'votinglog.html', {
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
        return render(request,'votinglog.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def votinglog_edit(request,pk):
    try:

        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            voter_records = user_response.json()
        else:
            voter_records = []


        ballot_response = call_get_method(BASEURL, 'delegate_nomination/ballot/', token)
        if ballot_response.status_code in [200,201]:
            ballot_records = ballot_response.json()
        else:
            ballot_records = []
    


        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        votinglog = call_get_method(BASEURL, f'delegate_nomination/votinglog/{pk}/',token)
        
        if votinglog.status_code in [200,201]:
            votinglog_data = votinglog.json()
        else:
            print('error------',votinglog)
            messages.error(request, 'Failed to retrieve data for votinglog. Please check your connection and try again.', extra_tags='warning')
            return redirect('votinglog')

        if request.method=="POST":
            form=VotingLogForm(request.POST,files = request.FILES, initial=votinglog_data,voter_choice=voter_records,ballot_choice=ballot_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'delegate_nomination/votinglog/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'votinglog successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('votinglog') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('votinglog_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = VotingLogForm(initial=votinglog_data,voter_choice=voter_records,ballot_choice=ballot_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('votinglog_edit.html', {'form': form, 'votinglog_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'votinglog_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def votinglog_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'delegate_nomination/votinglog/{pk}/'
        votinglog = call_delete_method(BASEURL, end_point,token)
        if votinglog.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for votinglog. Please try again.', extra_tags='warning')
            return redirect('votinglog')
        else:
            messages.success(request, 'Successfully deleted data for votinglog', extra_tags='success')
            return redirect('votinglog')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def votingresult(request):
    try:
        token = request.session['user_token']


        ballot_response = call_get_method(BASEURL, 'delegate_nomination/ballot/', token)
        if ballot_response.status_code in [200,201]:
            ballot_records = ballot_response.json()
        else:
            ballot_records = []
    
   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            nominee_records = user_response.json()
        else:
            nominee_records = []


        form=VotingResultForm(ballot_choice=ballot_records,nominee_choice=nominee_records)
        endpoint = 'delegate_nomination/votingresult/'
        if request.method=="POST":
            form=VotingResultForm(request.POST,files = request.FILES,ballot_choice=ballot_records,nominee_choice=nominee_records)
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
                    return redirect('votingresult')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('votingresult_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'votingresult.html', {
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
        return render(request,'votingresult.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def votingresult_edit(request,pk):
    try:

        token = request.session['user_token']


        ballot_response = call_get_method(BASEURL, 'delegate_nomination/ballot/', token)
        if ballot_response.status_code in [200,201]:
            ballot_records = ballot_response.json()
        else:
            ballot_records = []
    
   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            nominee_records = user_response.json()
        else:
            nominee_records = []



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        votingresult = call_get_method(BASEURL, f'delegate_nomination/votingresult/{pk}/',token)
        
        if votingresult.status_code in [200,201]:
            votingresult_data = votingresult.json()
        else:
            print('error------',votingresult)
            messages.error(request, 'Failed to retrieve data for votingresult. Please check your connection and try again.', extra_tags='warning')
            return redirect('votingresult')

        if request.method=="POST":
            form=VotingResultForm(request.POST,files = request.FILES, initial=votingresult_data,ballot_choice=ballot_records,nominee_choice=nominee_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'delegate_nomination/votingresult/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'votingresult successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('votingresult') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('votingresult_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = VotingResultForm(initial=votingresult_data,ballot_choice=ballot_records,nominee_choice=nominee_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('votingresult_edit.html', {'form': form, 'votingresult_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'votingresult_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def votingresult_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'delegate_nomination/votingresult/{pk}/'
        votingresult = call_delete_method(BASEURL, end_point,token)
        if votingresult.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for votingresult. Please try again.', extra_tags='warning')
            return redirect('votingresult')
        else:
            messages.success(request, 'Successfully deleted data for votingresult', extra_tags='success')
            return redirect('votingresult')

    except Exception as error:
        return render(request,'500.html',{'error':error})
