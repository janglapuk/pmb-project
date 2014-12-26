__author__ = 'janglapuk'

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', 'register.views.beranda', name='reg_beranda'),
    url(r'^login/$', 'register.views.user_login', name='reg_login'),
    url(r'^logout/$', 'register.views.user_logout', name='reg_logout'),
    url(r'^pmb/$', 'register.views.pmb', name='reg_pmb'),
    url(r'^pmb/submit/$', 'register.views.pmb_submit', name='reg_pmb_submit'),
    url(r'^pmb/success/(?P<kv>[A-F0-9]{8})/$', 'register.views.pmb_success', name='reg_pmb_success'),
    url(r'^pmb/json/(?P<data_key>\w+)/(?P<data_id>[\w\@\.\_]+)/$', 'register.views.pmb_json', name='reg_pmb_json'),
    url(r'^confirm/$', 'register.views.confirm', name='reg_confirm'),
    url(r'^confirm/success/$', 'register.views.confirm_success', name='reg_confirm_success'),
    url(r'^confirm/(?P<key_id>\w+)/$', 'register.views.confirm_submit', name='reg_confirm_submit'),
    url(r'^verify/$', 'register.views.verify', name='reg_verify'),
    url(r'^help/how-to-register/$', TemplateView.as_view(template_name='register/help/how-to.html'), name='reg_help_how_to'),
    url(r'^help/payment-information/$', TemplateView.as_view(template_name='register/help/payment-information.html'), name='reg_help_payment_info'),
    url(r'^help/about/$', TemplateView.as_view(template_name='register/help/about.html'), name='reg_help_about'),
    url(r'^help/contact/$', TemplateView.as_view(template_name='register/help/contact.html'), name='reg_help_contact'),
)
