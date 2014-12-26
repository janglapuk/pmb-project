from django.conf.urls import patterns, include, url
from django.contrib import admin

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webreg.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', lambda r: HttpResponseRedirect(reverse('reg_beranda'))),

    url(r'^register/', include('register.urls')),
    url(r'^administrator/', include('administrator.urls')),

    url(r'^djangoadmin/', include(admin.site.urls)),

)
