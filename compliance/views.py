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
def policy(request):
    try:
        token = request.session['user_token']


        form=PolicyForm()
        endpoint = 'compliance/policy/'
        if request.method=="POST":
            form=PolicyForm(request.POST,files = request.FILES,)
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
                    return redirect('policy')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('policy_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'policy.html', {
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
        return render(request,'policy.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def policy_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        policy = call_get_method(BASEURL, f'compliance/policy/{pk}/',token)
        
        if policy.status_code in [200,201]:
            policy_data = policy.json()
        else:
            print('error------',policy)
            messages.error(request, 'Failed to retrieve data for policy. Please check your connection and try again.', extra_tags='warning')
            return redirect('policy')

        if request.method=="POST":
            form=PolicyForm(request.POST,files = request.FILES, initial=policy_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/policy/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'policy successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('policy') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('policy_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = PolicyForm(initial=policy_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('policy_edit.html', {'form': form, 'policy_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'policy_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def policy_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/policy/{pk}/'
        policy = call_delete_method(BASEURL, end_point,token)
        if policy.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for policy. Please try again.', extra_tags='warning')
            return redirect('policy')
        else:
            messages.success(request, 'Successfully deleted data for policy', extra_tags='success')
            return redirect('policy')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def breach(request):
    try:
        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            reported_by_records = user_response.json()
        else:
            reported_by_records = []


        policy_response = call_get_method(BASEURL, 'compliance/policy/', token)
        if policy_response.status_code in [200,201]:
            policy_records = policy_response.json()
        else:
            policy_records = []
    

        form=BreachForm(reported_by_choice=reported_by_records,policy_choice=policy_records)
        endpoint = 'compliance/breach/'
        if request.method=="POST":
            form=BreachForm(request.POST,files = request.FILES,reported_by_choice=reported_by_records,policy_choice=policy_records)
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
                    return redirect('breach')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('breach_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'breach.html', {
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
        return render(request,'breach.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def breach_edit(request,pk):
    try:

        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            reported_by_records = user_response.json()
        else:
            reported_by_records = []


        policy_response = call_get_method(BASEURL, 'compliance/policy/', token)
        if policy_response.status_code in [200,201]:
            policy_records = policy_response.json()
        else:
            policy_records = []
    


        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        breach = call_get_method(BASEURL, f'compliance/breach/{pk}/',token)
        
        if breach.status_code in [200,201]:
            breach_data = breach.json()
        else:
            print('error------',breach)
            messages.error(request, 'Failed to retrieve data for breach. Please check your connection and try again.', extra_tags='warning')
            return redirect('breach')

        if request.method=="POST":
            form=BreachForm(request.POST,files = request.FILES, initial=breach_data,reported_by_choice=reported_by_records,policy_choice=policy_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/breach/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'breach successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('breach') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('breach_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = BreachForm(initial=breach_data,reported_by_choice=reported_by_records,policy_choice=policy_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('breach_edit.html', {'form': form, 'breach_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'breach_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def breach_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/breach/{pk}/'
        breach = call_delete_method(BASEURL, end_point,token)
        if breach.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for breach. Please try again.', extra_tags='warning')
            return redirect('breach')
        else:
            messages.success(request, 'Successfully deleted data for breach', extra_tags='success')
            return redirect('breach')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def staffpolicyacknowledgment(request):
    try:
        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            staff_records = user_response.json()
        else:
            staff_records = []


        policy_response = call_get_method(BASEURL, 'compliance/policy/', token)
        if policy_response.status_code in [200,201]:
            policy_records = policy_response.json()
        else:
            policy_records = []
    

        form=StaffPolicyAcknowledgmentForm(staff_choice=staff_records,policy_choice=policy_records)
        endpoint = 'compliance/staffpolicyacknowledgment/'
        if request.method=="POST":
            form=StaffPolicyAcknowledgmentForm(request.POST,files = request.FILES,staff_choice=staff_records,policy_choice=policy_records)
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
                    return redirect('staffpolicyacknowledgment')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('staffpolicyacknowledgment_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'staffpolicyacknowledgment.html', {
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
        return render(request,'staffpolicyacknowledgment.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def staffpolicyacknowledgment_edit(request,pk):
    try:

        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            staff_records = user_response.json()
        else:
            staff_records = []


        policy_response = call_get_method(BASEURL, 'compliance/policy/', token)
        if policy_response.status_code in [200,201]:
            policy_records = policy_response.json()
        else:
            policy_records = []
    


        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        staffpolicyacknowledgment = call_get_method(BASEURL, f'compliance/staffpolicyacknowledgment/{pk}/',token)
        
        if staffpolicyacknowledgment.status_code in [200,201]:
            staffpolicyacknowledgment_data = staffpolicyacknowledgment.json()
        else:
            print('error------',staffpolicyacknowledgment)
            messages.error(request, 'Failed to retrieve data for staffpolicyacknowledgment. Please check your connection and try again.', extra_tags='warning')
            return redirect('staffpolicyacknowledgment')

        if request.method=="POST":
            form=StaffPolicyAcknowledgmentForm(request.POST,files = request.FILES, initial=staffpolicyacknowledgment_data,staff_choice=staff_records,policy_choice=policy_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/staffpolicyacknowledgment/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'staffpolicyacknowledgment successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('staffpolicyacknowledgment') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('staffpolicyacknowledgment_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = StaffPolicyAcknowledgmentForm(initial=staffpolicyacknowledgment_data,staff_choice=staff_records,policy_choice=policy_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('staffpolicyacknowledgment_edit.html', {'form': form, 'staffpolicyacknowledgment_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'staffpolicyacknowledgment_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def staffpolicyacknowledgment_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/staffpolicyacknowledgment/{pk}/'
        staffpolicyacknowledgment = call_delete_method(BASEURL, end_point,token)
        if staffpolicyacknowledgment.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for staffpolicyacknowledgment. Please try again.', extra_tags='warning')
            return redirect('staffpolicyacknowledgment')
        else:
            messages.success(request, 'Successfully deleted data for staffpolicyacknowledgment', extra_tags='success')
            return redirect('staffpolicyacknowledgment')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def incident(request):
    try:
        token = request.session['user_token']


        related_breach_response = call_get_method(BASEURL, 'compliance/breach/', token)
        if related_breach_response.status_code in [200,201]:
            related_breach_records = related_breach_response.json()
        else:
            related_breach_records = []
    

        form=IncidentForm(related_breach_choice=related_breach_records)
        endpoint = 'compliance/incident/'
        if request.method=="POST":
            form=IncidentForm(request.POST,files = request.FILES,related_breach_choice=related_breach_records)
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
                    return redirect('incident')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('incident_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'incident.html', {
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
        return render(request,'incident.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def incident_edit(request,pk):
    try:

        token = request.session['user_token']


        related_breach_response = call_get_method(BASEURL, 'compliance/breach/', token)
        if related_breach_response.status_code in [200,201]:
            related_breach_records = related_breach_response.json()
        else:
            related_breach_records = []
    


        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        incident = call_get_method(BASEURL, f'compliance/incident/{pk}/',token)
        
        if incident.status_code in [200,201]:
            incident_data = incident.json()
        else:
            print('error------',incident)
            messages.error(request, 'Failed to retrieve data for incident. Please check your connection and try again.', extra_tags='warning')
            return redirect('incident')

        if request.method=="POST":
            form=IncidentForm(request.POST,files = request.FILES, initial=incident_data,related_breach_choice=related_breach_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/incident/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'incident successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('incident') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('incident_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = IncidentForm(initial=incident_data,related_breach_choice=related_breach_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('incident_edit.html', {'form': form, 'incident_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'incident_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def incident_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/incident/{pk}/'
        incident = call_delete_method(BASEURL, end_point,token)
        if incident.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for incident. Please try again.', extra_tags='warning')
            return redirect('incident')
        else:
            messages.success(request, 'Successfully deleted data for incident', extra_tags='success')
            return redirect('incident')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def correctiveaction(request):
    try:
        token = request.session['user_token']


        incident_response = call_get_method(BASEURL, 'compliance/incident/', token)
        if incident_response.status_code in [200,201]:
            incident_records = incident_response.json()
        else:
            incident_records = []
    

        form=CorrectiveActionForm(incident_choice=incident_records)
        endpoint = 'compliance/correctiveaction/'
        if request.method=="POST":
            form=CorrectiveActionForm(request.POST,files = request.FILES,incident_choice=incident_records)
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
                    return redirect('correctiveaction')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('correctiveaction_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'correctiveaction.html', {
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
        return render(request,'correctiveaction.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def correctiveaction_edit(request,pk):
    try:

        token = request.session['user_token']


        incident_response = call_get_method(BASEURL, 'compliance/incident/', token)
        if incident_response.status_code in [200,201]:
            incident_records = incident_response.json()
        else:
            incident_records = []
    


        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        correctiveaction = call_get_method(BASEURL, f'compliance/correctiveaction/{pk}/',token)
        
        if correctiveaction.status_code in [200,201]:
            correctiveaction_data = correctiveaction.json()
        else:
            print('error------',correctiveaction)
            messages.error(request, 'Failed to retrieve data for correctiveaction. Please check your connection and try again.', extra_tags='warning')
            return redirect('correctiveaction')

        if request.method=="POST":
            form=CorrectiveActionForm(request.POST,files = request.FILES, initial=correctiveaction_data,incident_choice=incident_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/correctiveaction/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'correctiveaction successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('correctiveaction') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('correctiveaction_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = CorrectiveActionForm(initial=correctiveaction_data,incident_choice=incident_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('correctiveaction_edit.html', {'form': form, 'correctiveaction_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'correctiveaction_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def correctiveaction_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/correctiveaction/{pk}/'
        correctiveaction = call_delete_method(BASEURL, end_point,token)
        if correctiveaction.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for correctiveaction. Please try again.', extra_tags='warning')
            return redirect('correctiveaction')
        else:
            messages.success(request, 'Successfully deleted data for correctiveaction', extra_tags='success')
            return redirect('correctiveaction')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def auditevidence(request):
    try:
        token = request.session['user_token']


        form=AuditEvidenceForm()
        endpoint = 'compliance/auditevidence/'
        if request.method=="POST":
            form=AuditEvidenceForm(request.POST,files = request.FILES,)
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
                    return redirect('auditevidence')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('auditevidence_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'auditevidence.html', {
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
        return render(request,'auditevidence.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def auditevidence_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        auditevidence = call_get_method(BASEURL, f'compliance/auditevidence/{pk}/',token)
        
        if auditevidence.status_code in [200,201]:
            auditevidence_data = auditevidence.json()
        else:
            print('error------',auditevidence)
            messages.error(request, 'Failed to retrieve data for auditevidence. Please check your connection and try again.', extra_tags='warning')
            return redirect('auditevidence')

        if request.method=="POST":
            form=AuditEvidenceForm(request.POST,files = request.FILES, initial=auditevidence_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/auditevidence/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'auditevidence successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('auditevidence') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('auditevidence_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = AuditEvidenceForm(initial=auditevidence_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('auditevidence_edit.html', {'form': form, 'auditevidence_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'auditevidence_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def auditevidence_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/auditevidence/{pk}/'
        auditevidence = call_delete_method(BASEURL, end_point,token)
        if auditevidence.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for auditevidence. Please try again.', extra_tags='warning')
            return redirect('auditevidence')
        else:
            messages.success(request, 'Successfully deleted data for auditevidence', extra_tags='success')
            return redirect('auditevidence')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def compliancecalendarevent(request):
    try:
        token = request.session['user_token']


        form=ComplianceCalendarEventForm()
        endpoint = 'compliance/compliancecalendarevent/'
        if request.method=="POST":
            form=ComplianceCalendarEventForm(request.POST,files = request.FILES,)
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
                    return redirect('compliancecalendarevent')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('compliancecalendarevent_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'compliancecalendarevent.html', {
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
        return render(request,'compliancecalendarevent.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def compliancecalendarevent_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        compliancecalendarevent = call_get_method(BASEURL, f'compliance/compliancecalendarevent/{pk}/',token)
        
        if compliancecalendarevent.status_code in [200,201]:
            compliancecalendarevent_data = compliancecalendarevent.json()
        else:
            print('error------',compliancecalendarevent)
            messages.error(request, 'Failed to retrieve data for compliancecalendarevent. Please check your connection and try again.', extra_tags='warning')
            return redirect('compliancecalendarevent')

        if request.method=="POST":
            form=ComplianceCalendarEventForm(request.POST,files = request.FILES, initial=compliancecalendarevent_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/compliancecalendarevent/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'compliancecalendarevent successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('compliancecalendarevent') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('compliancecalendarevent_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = ComplianceCalendarEventForm(initial=compliancecalendarevent_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('compliancecalendarevent_edit.html', {'form': form, 'compliancecalendarevent_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'compliancecalendarevent_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def compliancecalendarevent_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/compliancecalendarevent/{pk}/'
        compliancecalendarevent = call_delete_method(BASEURL, end_point,token)
        if compliancecalendarevent.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for compliancecalendarevent. Please try again.', extra_tags='warning')
            return redirect('compliancecalendarevent')
        else:
            messages.success(request, 'Successfully deleted data for compliancecalendarevent', extra_tags='success')
            return redirect('compliancecalendarevent')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def riskcontrolmatrix(request):
    try:
        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            owner_records = user_response.json()
        else:
            owner_records = []


        form=RiskControlMatrixForm(owner_choice=owner_records)
        endpoint = 'compliance/riskcontrolmatrix/'
        if request.method=="POST":
            form=RiskControlMatrixForm(request.POST,files = request.FILES,owner_choice=owner_records)
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
                    return redirect('riskcontrolmatrix')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('riskcontrolmatrix_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'riskcontrolmatrix.html', {
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
        return render(request,'riskcontrolmatrix.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def riskcontrolmatrix_edit(request,pk):
    try:

        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            owner_records = user_response.json()
        else:
            owner_records = []



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        riskcontrolmatrix = call_get_method(BASEURL, f'compliance/riskcontrolmatrix/{pk}/',token)
        
        if riskcontrolmatrix.status_code in [200,201]:
            riskcontrolmatrix_data = riskcontrolmatrix.json()
        else:
            print('error------',riskcontrolmatrix)
            messages.error(request, 'Failed to retrieve data for riskcontrolmatrix. Please check your connection and try again.', extra_tags='warning')
            return redirect('riskcontrolmatrix')

        if request.method=="POST":
            form=RiskControlMatrixForm(request.POST,files = request.FILES, initial=riskcontrolmatrix_data,owner_choice=owner_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/riskcontrolmatrix/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'riskcontrolmatrix successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('riskcontrolmatrix') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('riskcontrolmatrix_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = RiskControlMatrixForm(initial=riskcontrolmatrix_data,owner_choice=owner_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('riskcontrolmatrix_edit.html', {'form': form, 'riskcontrolmatrix_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'riskcontrolmatrix_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def riskcontrolmatrix_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/riskcontrolmatrix/{pk}/'
        riskcontrolmatrix = call_delete_method(BASEURL, end_point,token)
        if riskcontrolmatrix.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for riskcontrolmatrix. Please try again.', extra_tags='warning')
            return redirect('riskcontrolmatrix')
        else:
            messages.success(request, 'Successfully deleted data for riskcontrolmatrix', extra_tags='success')
            return redirect('riskcontrolmatrix')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def compliancereturn(request):
    try:
        token = request.session['user_token']


        form=ComplianceReturnForm()
        endpoint = 'compliance/compliancereturn/'
        if request.method=="POST":
            form=ComplianceReturnForm(request.POST,files = request.FILES,)
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
                    return redirect('compliancereturn')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('compliancereturn_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'compliancereturn.html', {
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
        return render(request,'compliancereturn.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def compliancereturn_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        compliancereturn = call_get_method(BASEURL, f'compliance/compliancereturn/{pk}/',token)
        
        if compliancereturn.status_code in [200,201]:
            compliancereturn_data = compliancereturn.json()
        else:
            print('error------',compliancereturn)
            messages.error(request, 'Failed to retrieve data for compliancereturn. Please check your connection and try again.', extra_tags='warning')
            return redirect('compliancereturn')

        if request.method=="POST":
            form=ComplianceReturnForm(request.POST,files = request.FILES, initial=compliancereturn_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/compliancereturn/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'compliancereturn successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('compliancereturn') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('compliancereturn_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = ComplianceReturnForm(initial=compliancereturn_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('compliancereturn_edit.html', {'form': form, 'compliancereturn_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'compliancereturn_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def compliancereturn_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/compliancereturn/{pk}/'
        compliancereturn = call_delete_method(BASEURL, end_point,token)
        if compliancereturn.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for compliancereturn. Please try again.', extra_tags='warning')
            return redirect('compliancereturn')
        else:
            messages.success(request, 'Successfully deleted data for compliancereturn', extra_tags='success')
            return redirect('compliancereturn')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def watchlistcheck(request):
    try:
        token = request.session['user_token']


        form=WatchlistCheckForm()
        endpoint = 'compliance/watchlistcheck/'
        if request.method=="POST":
            form=WatchlistCheckForm(request.POST,files = request.FILES,)
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
                    return redirect('watchlistcheck')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('watchlistcheck_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'watchlistcheck.html', {
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
        return render(request,'watchlistcheck.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def watchlistcheck_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        watchlistcheck = call_get_method(BASEURL, f'compliance/watchlistcheck/{pk}/',token)
        
        if watchlistcheck.status_code in [200,201]:
            watchlistcheck_data = watchlistcheck.json()
        else:
            print('error------',watchlistcheck)
            messages.error(request, 'Failed to retrieve data for watchlistcheck. Please check your connection and try again.', extra_tags='warning')
            return redirect('watchlistcheck')

        if request.method=="POST":
            form=WatchlistCheckForm(request.POST,files = request.FILES, initial=watchlistcheck_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'compliance/watchlistcheck/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'watchlistcheck successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('watchlistcheck') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('watchlistcheck_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = WatchlistCheckForm(initial=watchlistcheck_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('watchlistcheck_edit.html', {'form': form, 'watchlistcheck_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'watchlistcheck_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def watchlistcheck_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'compliance/watchlistcheck/{pk}/'
        watchlistcheck = call_delete_method(BASEURL, end_point,token)
        if watchlistcheck.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for watchlistcheck. Please try again.', extra_tags='warning')
            return redirect('watchlistcheck')
        else:
            messages.success(request, 'Successfully deleted data for watchlistcheck', extra_tags='success')
            return redirect('watchlistcheck')

    except Exception as error:
        return render(request,'500.html',{'error':error})
