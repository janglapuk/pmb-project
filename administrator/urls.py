__author__ = 'janglapuk'

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', 'administrator.views.adm_beranda', name='adm_beranda'),
    url(r'^registrations/(?P<key_id>\w+)/$', 'administrator.views.adm_registrations', name='adm_registrations'),
    url(r'^payments/(?P<key_id>\w+)/$', 'administrator.views.adm_payments', name='adm_payments'),
    url(r'^json/(?P<key_id>\w+).json$', 'administrator.views.adm_json', name='adm_json'),
    url(r'^ajax/(?P<action>\w+)/(?P<key_id>\w+)/$', 'administrator.views.adm_ajax', name='adm_ajax'),
    url(r'^login/$', 'administrator.views.adm_login', name='adm_login'),
    url(r'^logout/$', 'administrator.views.adm_logout', name='adm_logout'),

    url(r'^settings/general/$', 'administrator.views.adm_settings_general', name='adm_settings_general'),
    url(r'^settings/academic/$', 'administrator.views.adm_settings_academic', name='adm_settings_academic'),
    url(r'^settings/administration/$', 'administrator.views.adm_settings_administration', name='adm_settings_administration'),
    url(r'^settings/users/$', 'administrator.views.adm_settings_users', name='adm_settings_users'),
)