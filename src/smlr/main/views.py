from datetime import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson

try:
    import simplejson
except:
    import json as simplejson

from smlr.main.models import URL, Redirect
from smlr.main.forms import URLForm
from smlr.main.utils import *


def index(request):
    url = None
    
    if request.method == 'POST':
        form = URLForm(request.POST)
        
        if form.is_valid():
            url = None
            
            if form.cleaned_data['alias']:
                url = URL.objects.create(   original_url=form.cleaned_data['long_url'],
                                            alias=form.cleaned_data['alias'],
                                            is_custom_alias=True)   
            else:
                url = URL.objects.create(original_url=form.cleaned_data['long_url'])

                potential_alias = base36encode(url.id)
                qs = URL.objects.filter(alias=potential_alias)
                counter = 1

                while qs:
                    potential_alias = base36encode(url.id + counter)
                    qs = URL.objects.filter(alias=potential_alias)
                    counter += 1

                url.alias = potential_alias

            url.save()
            
            long_url = form.cleaned_data['long_url']
            short_url = "http://" + request.META['HTTP_HOST'] + "/" + url.alias
    else:
        form = URLForm()
    
    return render_to_response('index.html', {
        'form': form,
        'url': url,
    })


def reverse(request, alias):
    try:
        url = URL.objects.get(alias=alias)
    except URL.DoesNotExist:
        return HttpResponseRedirect("/")
    
    redirect = Redirect()
    redirect.url = url
    redirect.user_agent = request.META.get('HTTP_USER_AGENT', None)
    redirect.remote_host = request.META.get('REMOTE_HOST', None)
    redirect.remote_ip = request.META.get('REMOTE_ADDR', None)
    redirect.remote_port = request.META.get('REMOTE_PORT', None)
    redirect.request_method = request.META.get('REQUEST_METHOD', None)
    redirect.save()
    
    return HttpResponseRedirect(url.original_url)


def stats(request, alias):
    try:
        url = URL.objects.get(alias=alias)
    except:
        return HttpResponseRedirect("/")

    original_url = url.original_url
    short_url = url.get_short_url()
    
    reduction_chars = len(original_url) - len(short_url)
    reduction_percent = 100 - int(round((float(len(short_url)) /
                                float(len(original_url))) * 100))
                                
    redirects = url.redirect_set.count()
    shortenings = url.shortenings
    
    return render_to_response('stats.html', locals())


def api_shorten(request):
    if request.method != 'POST':
        return HttpResponse(simplejson.dumps({
            'status': 'error',
            'message': 'Request must be a POST'
        }), mimetype="application/json")
    
    if 'url' not in request.POST:
        return HttpResponse(simplejson.dumps({
            'status': 'error',
            'message': 'You must provide a url to shorten.'
        }), mimetype="application/json")
        
    long_url = request.POST.get('url', None)
    alias = request.POST.get('alias', None)
    
    if not long_url:
        return HttpResponse(simplejson.dumps({
            'status': 'error',
            'message': 'You must provide a url to shorten.'
        }), mimetype="application/json")
            
    if alias:
        if len(alias) > 8:
            return HttpResponse(simplejson.dumps({
                'status': 'error',
                'message': 'Alias must be no more than 8 characters.'
            }), mimetype="application/json")
        
        url = URL.objects.create(   original_url=long_url,
                                    alias=alias,
                                    is_custom_alias=True)
    else:
        url = URL.objects.create(original_url=long_url)

        potential_alias = base36encode(url.id)
        qs = URL.objects.filter(alias=potential_alias)
        counter = 1

        while qs:
            potential_alias = base36encode(url.id + counter)
            qs = URL.objects.filter(alias=potential_alias)
            counter += 1

        url.alias = potential_alias

    url.save()

    short_url = "http://" + request.META['HTTP_HOST'] + "/" + url.alias
    
    return HttpResponse(simplejson.dumps({
        'status': 'ok',
        'message': 'URL shortened.',
        'long_url': long_url,
        'short_url': short_url
    }), mimetype="application/json") 


def api_stats(request):
    return HttpResponse(simplejson.dumps({
        'status': 'error',
        'message': 'Not yet implemented.'
    }), mimetype="application/json")


def api_test(request):
    return render_to_response('test-api.html')
