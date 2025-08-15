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
def socialpost(request):
    try:
        token = request.session['user_token']


        form=SocialPostForm()
        endpoint = 'advertising/socialpost/'
        if request.method=="POST":
            form=SocialPostForm(request.POST,files = request.FILES,)
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
                    return redirect('socialpost')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('socialpost_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'socialpost.html', {
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
        return render(request,'socialpost.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def socialpost_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        socialpost = call_get_method(BASEURL, f'advertising/socialpost/{pk}/',token)
        
        if socialpost.status_code in [200,201]:
            socialpost_data = socialpost.json()
        else:
            print('error------',socialpost)
            messages.error(request, 'Failed to retrieve data for socialpost. Please check your connection and try again.', extra_tags='warning')
            return redirect('socialpost')

        if request.method=="POST":
            form=SocialPostForm(request.POST,files = request.FILES, initial=socialpost_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'advertising/socialpost/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'socialpost successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('socialpost') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('socialpost_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = SocialPostForm(initial=socialpost_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('socialpost_edit.html', {'form': form, 'socialpost_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'socialpost_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def socialpost_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'advertising/socialpost/{pk}/'
        socialpost = call_delete_method(BASEURL, end_point,token)
        if socialpost.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for socialpost. Please try again.', extra_tags='warning')
            return redirect('socialpost')
        else:
            messages.success(request, 'Successfully deleted data for socialpost', extra_tags='success')
            return redirect('socialpost')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def compliancebanner(request):
    try:
        token = request.session['user_token']


        form=ComplianceBannerForm()
        endpoint = 'advertising/compliancebanner/'
        if request.method=="POST":
            form=ComplianceBannerForm(request.POST,files = request.FILES,)
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
                    return redirect('compliancebanner')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('compliancebanner_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'compliancebanner.html', {
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
        return render(request,'compliancebanner.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def compliancebanner_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        compliancebanner = call_get_method(BASEURL, f'advertising/compliancebanner/{pk}/',token)
        
        if compliancebanner.status_code in [200,201]:
            compliancebanner_data = compliancebanner.json()
        else:
            print('error------',compliancebanner)
            messages.error(request, 'Failed to retrieve data for compliancebanner. Please check your connection and try again.', extra_tags='warning')
            return redirect('compliancebanner')

        if request.method=="POST":
            form=ComplianceBannerForm(request.POST,files = request.FILES, initial=compliancebanner_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'advertising/compliancebanner/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'compliancebanner successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('compliancebanner') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('compliancebanner_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = ComplianceBannerForm(initial=compliancebanner_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('compliancebanner_edit.html', {'form': form, 'compliancebanner_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'compliancebanner_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def compliancebanner_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'advertising/compliancebanner/{pk}/'
        compliancebanner = call_delete_method(BASEURL, end_point,token)
        if compliancebanner.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for compliancebanner. Please try again.', extra_tags='warning')
            return redirect('compliancebanner')
        else:
            messages.success(request, 'Successfully deleted data for compliancebanner', extra_tags='success')
            return redirect('compliancebanner')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def contentitem(request):
    try:
        token = request.session['user_token']


        form=ContentItemForm()
        endpoint = 'advertising/contentitem/'
        if request.method=="POST":
            form=ContentItemForm(request.POST,files = request.FILES,)
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
                    return redirect('contentitem')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('contentitem_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'contentitem.html', {
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
        return render(request,'contentitem.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def contentitem_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        contentitem = call_get_method(BASEURL, f'advertising/contentitem/{pk}/',token)
        
        if contentitem.status_code in [200,201]:
            contentitem_data = contentitem.json()
        else:
            print('error------',contentitem)
            messages.error(request, 'Failed to retrieve data for contentitem. Please check your connection and try again.', extra_tags='warning')
            return redirect('contentitem')

        if request.method=="POST":
            form=ContentItemForm(request.POST,files = request.FILES, initial=contentitem_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'advertising/contentitem/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'contentitem successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('contentitem') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('contentitem_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = ContentItemForm(initial=contentitem_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('contentitem_edit.html', {'form': form, 'contentitem_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'contentitem_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def contentitem_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'advertising/contentitem/{pk}/'
        contentitem = call_delete_method(BASEURL, end_point,token)
        if contentitem.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for contentitem. Please try again.', extra_tags='warning')
            return redirect('contentitem')
        else:
            messages.success(request, 'Successfully deleted data for contentitem', extra_tags='success')
            return redirect('contentitem')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def subscription(request):
    try:
        token = request.session['user_token']


        form=SubscriptionForm()
        endpoint = 'advertising/subscription/'
        if request.method=="POST":
            form=SubscriptionForm(request.POST,files = request.FILES,)
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
                    return redirect('subscription')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('subscription_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'subscription.html', {
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
        return render(request,'subscription.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def subscription_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        subscription = call_get_method(BASEURL, f'advertising/subscription/{pk}/',token)
        
        if subscription.status_code in [200,201]:
            subscription_data = subscription.json()
        else:
            print('error------',subscription)
            messages.error(request, 'Failed to retrieve data for subscription. Please check your connection and try again.', extra_tags='warning')
            return redirect('subscription')

        if request.method=="POST":
            form=SubscriptionForm(request.POST,files = request.FILES, initial=subscription_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'advertising/subscription/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'subscription successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('subscription') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('subscription_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = SubscriptionForm(initial=subscription_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('subscription_edit.html', {'form': form, 'subscription_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'subscription_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def subscription_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'advertising/subscription/{pk}/'
        subscription = call_delete_method(BASEURL, end_point,token)
        if subscription.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for subscription. Please try again.', extra_tags='warning')
            return redirect('subscription')
        else:
            messages.success(request, 'Successfully deleted data for subscription', extra_tags='success')
            return redirect('subscription')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def mediaasset(request):
    try:
        token = request.session['user_token']


        form=MediaAssetForm()
        endpoint = 'advertising/mediaasset/'
        if request.method=="POST":
            form=MediaAssetForm(request.POST,files = request.FILES,)
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
                    return redirect('mediaasset')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('mediaasset_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'mediaasset.html', {
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
        return render(request,'mediaasset.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def mediaasset_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        mediaasset = call_get_method(BASEURL, f'advertising/mediaasset/{pk}/',token)
        
        if mediaasset.status_code in [200,201]:
            mediaasset_data = mediaasset.json()
        else:
            print('error------',mediaasset)
            messages.error(request, 'Failed to retrieve data for mediaasset. Please check your connection and try again.', extra_tags='warning')
            return redirect('mediaasset')

        if request.method=="POST":
            form=MediaAssetForm(request.POST,files = request.FILES, initial=mediaasset_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'advertising/mediaasset/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'mediaasset successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('mediaasset') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('mediaasset_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = MediaAssetForm(initial=mediaasset_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('mediaasset_edit.html', {'form': form, 'mediaasset_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'mediaasset_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def mediaasset_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'advertising/mediaasset/{pk}/'
        mediaasset = call_delete_method(BASEURL, end_point,token)
        if mediaasset.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for mediaasset. Please try again.', extra_tags='warning')
            return redirect('mediaasset')
        else:
            messages.success(request, 'Successfully deleted data for mediaasset', extra_tags='success')
            return redirect('mediaasset')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def adbooking(request):
    try:
        token = request.session['user_token']


        form=AdBookingForm()
        endpoint = 'advertising/adbooking/'
        if request.method=="POST":
            form=AdBookingForm(request.POST,files = request.FILES,)
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
                    return redirect('adbooking')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('adbooking_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'adbooking.html', {
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
        return render(request,'adbooking.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def adbooking_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        adbooking = call_get_method(BASEURL, f'advertising/adbooking/{pk}/',token)
        
        if adbooking.status_code in [200,201]:
            adbooking_data = adbooking.json()
        else:
            print('error------',adbooking)
            messages.error(request, 'Failed to retrieve data for adbooking. Please check your connection and try again.', extra_tags='warning')
            return redirect('adbooking')

        if request.method=="POST":
            form=AdBookingForm(request.POST,files = request.FILES, initial=adbooking_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'advertising/adbooking/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'adbooking successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('adbooking') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('adbooking_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = AdBookingForm(initial=adbooking_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('adbooking_edit.html', {'form': form, 'adbooking_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'adbooking_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def adbooking_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'advertising/adbooking/{pk}/'
        adbooking = call_delete_method(BASEURL, end_point,token)
        if adbooking.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for adbooking. Please try again.', extra_tags='warning')
            return redirect('adbooking')
        else:
            messages.success(request, 'Successfully deleted data for adbooking', extra_tags='success')
            return redirect('adbooking')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def newsletter(request):
    try:
        token = request.session['user_token']


        form=NewsletterForm()
        endpoint = 'advertising/newsletter/'
        if request.method=="POST":
            form=NewsletterForm(request.POST,files = request.FILES,)
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
                    return redirect('newsletter')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('newsletter_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'newsletter.html', {
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
        return render(request,'newsletter.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def newsletter_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        newsletter = call_get_method(BASEURL, f'advertising/newsletter/{pk}/',token)
        
        if newsletter.status_code in [200,201]:
            newsletter_data = newsletter.json()
        else:
            print('error------',newsletter)
            messages.error(request, 'Failed to retrieve data for newsletter. Please check your connection and try again.', extra_tags='warning')
            return redirect('newsletter')

        if request.method=="POST":
            form=NewsletterForm(request.POST,files = request.FILES, initial=newsletter_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'advertising/newsletter/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'newsletter successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('newsletter') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('newsletter_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = NewsletterForm(initial=newsletter_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('newsletter_edit.html', {'form': form, 'newsletter_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'newsletter_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def newsletter_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'advertising/newsletter/{pk}/'
        newsletter = call_delete_method(BASEURL, end_point,token)
        if newsletter.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for newsletter. Please try again.', extra_tags='warning')
            return redirect('newsletter')
        else:
            messages.success(request, 'Successfully deleted data for newsletter', extra_tags='success')
            return redirect('newsletter')

    except Exception as error:
        return render(request,'500.html',{'error':error})
# create and view table function
@custom_login_required
def webanalytics(request):
    try:
        token = request.session['user_token']


        form=WebAnalyticsForm()
        endpoint = 'advertising/webanalytics/'
        if request.method=="POST":
            form=WebAnalyticsForm(request.POST,files = request.FILES,)
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
                    return redirect('webanalytics')

                else:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': response.json()})
                    messages.error(request, 'Error saving data', extra_tags='danger')
        else:
            print('errorss',form.errors)

            # AJAX request with invalid form
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string('webanalytics_edit.html', {'form': form}, request=request)
                return JsonResponse({'success': False, 'formHtml': html})
            # non-AJAX fallback — fall through to render below

        try:
            # getting data from backend
            records_response = call_get_method(BASEURL,endpoint,token)
            if records_response.status_code in [200,201]:
                records = records_response.json()
                return render(request, 'webanalytics.html', {
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
        return render(request,'webanalytics.html',context)

    except Exception as error:
        return render(request,'500.html',{'error':error})

# edit function
@custom_login_required
def webanalytics_edit(request,pk):
    try:

        token = request.session['user_token']



        mode = request.GET.get('mode', 'edit')  # default to edit if not provided
        webanalytics = call_get_method(BASEURL, f'advertising/webanalytics/{pk}/',token)
        
        if webanalytics.status_code in [200,201]:
            webanalytics_data = webanalytics.json()
        else:
            print('error------',webanalytics)
            messages.error(request, 'Failed to retrieve data for webanalytics. Please check your connection and try again.', extra_tags='warning')
            return redirect('webanalytics')

        if request.method=="POST":
            form=WebAnalyticsForm(request.POST,files = request.FILES, initial=webanalytics_data,)
            if form.is_valid():
                updated_data = form.cleaned_data
                updated_data['id'] = pk
                for field_name, field in form.fields.items():
                    if isinstance(field.widget, forms.DateInput) or isinstance(field, (forms.DateField, forms.DateTimeField, forms.DecimalField, forms.TimeField)):
                        if updated_data.get(field_name):
                            updated_data[field_name] = request.POST.get(field_name)

                # Serialize the updated data as JSON
                json_data = json.dumps(updated_data)
                response = call_put_method(BASEURL, f'advertising/webanalytics/{pk}/', json_data,token)

                if response.status_code in [200,201]: 
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True})
                    messages.success(request, 'webanalytics successfully updated.', extra_tags='success')
                    # messages.success(request, 'Your data has been successfully saved', extra_tags='success')
                    return redirect('webanalytics') 
                else:
                    error_message = response.json()
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': error_message})
                    messages.error(request, f"Oops..! {error_message}", extra_tags='warning')
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    html = render_to_string('webanalytics_edit.html', {'form': form,'mode': mode}, request=request)
                    return JsonResponse({'success': False, 'formHtml': html})
                messages.error(request, "Form validation failed.", extra_tags='danger')
                print("An error occurred: Expecting value: line 1 column 1 (char 0)")
        else:
            form = WebAnalyticsForm(initial=webanalytics_data,)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('webanalytics_edit.html', {'form': form, 'webanalytics_id': pk,'mode': mode}, request=request)
            return HttpResponse(html)

        context={
            'form':form
        }
        return render(request,'webanalytics_edit.html',context)
    except Exception as error:
        return render(request,'500.html',{'error':error})


@custom_login_required
def webanalytics_delete(request,pk):
    try:
        token = request.session['user_token']
        end_point = f'advertising/webanalytics/{pk}/'
        webanalytics = call_delete_method(BASEURL, end_point,token)
        if webanalytics.status_code in [200,201]:
            messages.error(request, 'Failed to delete data for webanalytics. Please try again.', extra_tags='warning')
            return redirect('webanalytics')
        else:
            messages.success(request, 'Successfully deleted data for webanalytics', extra_tags='success')
            return redirect('webanalytics')

    except Exception as error:
        return render(request,'500.html',{'error':error})
