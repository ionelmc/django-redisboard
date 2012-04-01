from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'redisboard_sample_project.views.home', name='home'),
    # url(r'^redisboard_sample_project/', include('redisboard_sample_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^', include(admin.site.urls)),
)
