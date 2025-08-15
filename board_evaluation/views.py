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
def boardmeeting(request):
    try:
        token = request.session['user_token']


        form=BoardMeetingForm()
        endpoint = 'board_evaluation/boardmeeting/'
        if request.method=="POST":
            form=BoardMeetingForm(request.POST,files = request.FILES,)
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
                    return redirect('boardmeeting')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('boardmeeting_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'boardmeeting.html', {
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
        return render(request,'boardmeeting.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def boardmeeting_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        boardmeeting = call_get_method(BASEURL, f'board_evaluation/boardmeeting/{pk}/',token)
        
        if boardmeeting.status_code in [200,201]:
            boardmeeting_data = boardmeeting.json()
        else:
            print('error------',boardmeeting)
            messages.error(request, 'Failed to retrieve data for boardmeeting. Please check your connection and try again.', extra_tags='warning')
            return redirect('boardmeeting')

        if request.method=="POST":
            form=BoardMeetingForm(request.POST,files = request.FILES, initial=boardmeeting_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'board_evaluation/boardmeeting/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'boardmeeting successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('boardmeeting') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('boardmeeting_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = BoardMeetingForm(initial=boardmeeting_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('boardmeeting_edit.html', {'form': form, 'boardmeeting_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'boardmeeting_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def boardmeeting_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'board_evaluation/boardmeeting/{pk}/'
        boardmeeting = call_delete_method(BASEURL, end_point,token)
        if boardmeeting.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for boardmeeting. Please try again.', extra_tags='warning')
            return redirect('boardmeeting')
        else:
            messages.success(request, 'Successfully deleted data for boardmeeting', extra_tags='success')
            return redirect('boardmeeting')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def actionitem(request):
    try:
        token = request.session['user_token']


        board_meeting_response = call_get_method(BASEURL, 'board_evaluation/boardmeeting/', token)
        if board_meeting_response.status_code in [200,201]:
            board_meeting_records = board_meeting_response.json()
        else:
            board_meeting_records = []
    
   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            owner_records = user_response.json()
        else:
            owner_records = []


        form=ActionItemForm(board_meeting_choice=board_meeting_records,owner_choice=owner_records)
        endpoint = 'board_evaluation/actionitem/'
        if request.method=="POST":
            form=ActionItemForm(request.POST,files = request.FILES,board_meeting_choice=board_meeting_records,owner_choice=owner_records)
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
                    return redirect('actionitem')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('actionitem_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'actionitem.html', {
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
        return render(request,'actionitem.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def actionitem_edit(request,pk):
    try:

        token = request.session['user_token']


        board_meeting_response = call_get_method(BASEURL, 'board_evaluation/boardmeeting/', token)
        if board_meeting_response.status_code in [200,201]:
            board_meeting_records = board_meeting_response.json()
        else:
            board_meeting_records = []
    
   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            owner_records = user_response.json()
        else:
            owner_records = []



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        actionitem = call_get_method(BASEURL, f'board_evaluation/actionitem/{pk}/',token)
        
        if actionitem.status_code in [200,201]:
            actionitem_data = actionitem.json()
        else:
            print('error------',actionitem)
            messages.error(request, 'Failed to retrieve data for actionitem. Please check your connection and try again.', extra_tags='warning')
            return redirect('actionitem')

        if request.method=="POST":
            form=ActionItemForm(request.POST,files = request.FILES, initial=actionitem_data,board_meeting_choice=board_meeting_records,owner_choice=owner_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'board_evaluation/actionitem/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'actionitem successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('actionitem') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('actionitem_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = ActionItemForm(initial=actionitem_data,board_meeting_choice=board_meeting_records,owner_choice=owner_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('actionitem_edit.html', {'form': form, 'actionitem_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'actionitem_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def actionitem_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'board_evaluation/actionitem/{pk}/'
        actionitem = call_delete_method(BASEURL, end_point,token)
        if actionitem.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for actionitem. Please try again.', extra_tags='warning')
            return redirect('actionitem')
        else:
            messages.success(request, 'Successfully deleted data for actionitem', extra_tags='success')
            return redirect('actionitem')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def decisionlog(request):
    try:
        token = request.session['user_token']


        board_meeting_response = call_get_method(BASEURL, 'board_evaluation/boardmeeting/', token)
        if board_meeting_response.status_code in [200,201]:
            board_meeting_records = board_meeting_response.json()
        else:
            board_meeting_records = []
    
   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            decision_made_by_records = user_response.json()
        else:
            decision_made_by_records = []


        form=DecisionLogForm(board_meeting_choice=board_meeting_records,decision_made_by_choice=decision_made_by_records)
        endpoint = 'board_evaluation/decisionlog/'
        if request.method=="POST":
            form=DecisionLogForm(request.POST,files = request.FILES,board_meeting_choice=board_meeting_records,decision_made_by_choice=decision_made_by_records)
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
                    return redirect('decisionlog')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('decisionlog_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'decisionlog.html', {
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
        return render(request,'decisionlog.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def decisionlog_edit(request,pk):
    try:

        token = request.session['user_token']


        board_meeting_response = call_get_method(BASEURL, 'board_evaluation/boardmeeting/', token)
        if board_meeting_response.status_code in [200,201]:
            board_meeting_records = board_meeting_response.json()
        else:
            board_meeting_records = []
    
   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            decision_made_by_records = user_response.json()
        else:
            decision_made_by_records = []



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        decisionlog = call_get_method(BASEURL, f'board_evaluation/decisionlog/{pk}/',token)
        
        if decisionlog.status_code in [200,201]:
            decisionlog_data = decisionlog.json()
        else:
            print('error------',decisionlog)
            messages.error(request, 'Failed to retrieve data for decisionlog. Please check your connection and try again.', extra_tags='warning')
            return redirect('decisionlog')

        if request.method=="POST":
            form=DecisionLogForm(request.POST,files = request.FILES, initial=decisionlog_data,board_meeting_choice=board_meeting_records,decision_made_by_choice=decision_made_by_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'board_evaluation/decisionlog/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'decisionlog successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('decisionlog') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('decisionlog_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = DecisionLogForm(initial=decisionlog_data,board_meeting_choice=board_meeting_records,decision_made_by_choice=decision_made_by_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('decisionlog_edit.html', {'form': form, 'decisionlog_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'decisionlog_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def decisionlog_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'board_evaluation/decisionlog/{pk}/'
        decisionlog = call_delete_method(BASEURL, end_point,token)
        if decisionlog.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for decisionlog. Please try again.', extra_tags='warning')
            return redirect('decisionlog')
        else:
            messages.success(request, 'Successfully deleted data for decisionlog', extra_tags='success')
            return redirect('decisionlog')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def conflictofinterest(request):
    try:
        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            board_member_records = user_response.json()
        else:
            board_member_records = []


        form=ConflictOfInterestForm(board_member_choice=board_member_records)
        endpoint = 'board_evaluation/conflictofinterest/'
        if request.method=="POST":
            form=ConflictOfInterestForm(request.POST,files = request.FILES,board_member_choice=board_member_records)
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
                    return redirect('conflictofinterest')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('conflictofinterest_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'conflictofinterest.html', {
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
        return render(request,'conflictofinterest.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def conflictofinterest_edit(request,pk):
    try:

        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            board_member_records = user_response.json()
        else:
            board_member_records = []



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        conflictofinterest = call_get_method(BASEURL, f'board_evaluation/conflictofinterest/{pk}/',token)
        
        if conflictofinterest.status_code in [200,201]:
            conflictofinterest_data = conflictofinterest.json()
        else:
            print('error------',conflictofinterest)
            messages.error(request, 'Failed to retrieve data for conflictofinterest. Please check your connection and try again.', extra_tags='warning')
            return redirect('conflictofinterest')

        if request.method=="POST":
            form=ConflictOfInterestForm(request.POST,files = request.FILES, initial=conflictofinterest_data,board_member_choice=board_member_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'board_evaluation/conflictofinterest/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'conflictofinterest successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('conflictofinterest') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('conflictofinterest_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = ConflictOfInterestForm(initial=conflictofinterest_data,board_member_choice=board_member_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('conflictofinterest_edit.html', {'form': form, 'conflictofinterest_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'conflictofinterest_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def conflictofinterest_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'board_evaluation/conflictofinterest/{pk}/'
        conflictofinterest = call_delete_method(BASEURL, end_point,token)
        if conflictofinterest.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for conflictofinterest. Please try again.', extra_tags='warning')
            return redirect('conflictofinterest')
        else:
            messages.success(request, 'Successfully deleted data for conflictofinterest', extra_tags='success')
            return redirect('conflictofinterest')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def boardkpi(request):
    try:
        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            board_member_records = user_response.json()
        else:
            board_member_records = []


        form=BoardKPIForm(board_member_choice=board_member_records)
        endpoint = 'board_evaluation/boardkpi/'
        if request.method=="POST":
            form=BoardKPIForm(request.POST,files = request.FILES,board_member_choice=board_member_records)
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
                    return redirect('boardkpi')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('boardkpi_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'boardkpi.html', {
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
        return render(request,'boardkpi.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def boardkpi_edit(request,pk):
    try:

        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            board_member_records = user_response.json()
        else:
            board_member_records = []



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        boardkpi = call_get_method(BASEURL, f'board_evaluation/boardkpi/{pk}/',token)
        
        if boardkpi.status_code in [200,201]:
            boardkpi_data = boardkpi.json()
        else:
            print('error------',boardkpi)
            messages.error(request, 'Failed to retrieve data for boardkpi. Please check your connection and try again.', extra_tags='warning')
            return redirect('boardkpi')

        if request.method=="POST":
            form=BoardKPIForm(request.POST,files = request.FILES, initial=boardkpi_data,board_member_choice=board_member_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'board_evaluation/boardkpi/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'boardkpi successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('boardkpi') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('boardkpi_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = BoardKPIForm(initial=boardkpi_data,board_member_choice=board_member_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('boardkpi_edit.html', {'form': form, 'boardkpi_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'boardkpi_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def boardkpi_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'board_evaluation/boardkpi/{pk}/'
        boardkpi = call_delete_method(BASEURL, end_point,token)
        if boardkpi.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for boardkpi. Please try again.', extra_tags='warning')
            return redirect('boardkpi')
        else:
            messages.success(request, 'Successfully deleted data for boardkpi', extra_tags='success')
            return redirect('boardkpi')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def boardevaluation(request):
    try:
        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            board_member_records = user_response.json()
        else:
            board_member_records = []

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            evaluator_records = user_response.json()
        else:
            evaluator_records = []


        form=BoardEvaluationForm(board_member_choice=board_member_records,evaluator_choice=evaluator_records)
        endpoint = 'board_evaluation/boardevaluation/'
        if request.method=="POST":
            form=BoardEvaluationForm(request.POST,files = request.FILES,board_member_choice=board_member_records,evaluator_choice=evaluator_records)
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
                    return redirect('boardevaluation')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('boardevaluation_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'boardevaluation.html', {
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
        return render(request,'boardevaluation.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def boardevaluation_edit(request,pk):
    try:

        token = request.session['user_token']

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            board_member_records = user_response.json()
        else:
            board_member_records = []

   

        user_response = call_get_method(BASEURL,'user_management/user/',token)
        if user_response.status_code in [200,201]:
            evaluator_records = user_response.json()
        else:
            evaluator_records = []



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        boardevaluation = call_get_method(BASEURL, f'board_evaluation/boardevaluation/{pk}/',token)
        
        if boardevaluation.status_code in [200,201]:
            boardevaluation_data = boardevaluation.json()
        else:
            print('error------',boardevaluation)
            messages.error(request, 'Failed to retrieve data for boardevaluation. Please check your connection and try again.', extra_tags='warning')
            return redirect('boardevaluation')

        if request.method=="POST":
            form=BoardEvaluationForm(request.POST,files = request.FILES, initial=boardevaluation_data,board_member_choice=board_member_records,evaluator_choice=evaluator_records)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'board_evaluation/boardevaluation/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'boardevaluation successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('boardevaluation') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('boardevaluation_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = BoardEvaluationForm(initial=boardevaluation_data,board_member_choice=board_member_records,evaluator_choice=evaluator_records)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('boardevaluation_edit.html', {'form': form, 'boardevaluation_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'boardevaluation_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def boardevaluation_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'board_evaluation/boardevaluation/{pk}/'
        boardevaluation = call_delete_method(BASEURL, end_point,token)
        if boardevaluation.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for boardevaluation. Please try again.', extra_tags='warning')
            return redirect('boardevaluation')
        else:
            messages.success(request, 'Successfully deleted data for boardevaluation', extra_tags='success')
            return redirect('boardevaluation')

    except Exception as error:
        return render(request,'500.html',{'error':error})
