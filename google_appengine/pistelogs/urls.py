from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'pistelogs.views.index'),
    (r'^profile/(.*)', 'pistelogs.views.user_profile'),    
    (r'^(.*)/run/(.*)', 'pistelogs.views.user_run'),
    # instructions
    (r'^instructions/', 'pistelogs.views.instructions'),
    # oob
    (r'^oob/', 'pistelogs.views.oob'),
    # resorts
    (r'^resorts/', 'pistelogs.views.resorts'),
    (r'^resort/(.*)', 'pistelogs.views.resort'),
    # docs
    (r'^apidocs/', 'pistelogs.views.apidocs'),
    #(r'^admin/', include('django.contrib.admin.urls')),
    ######
    # API
    ######
    (r'^api/depositlog', 'pistelogs.views.receive_log'),
    # the most recently used layout
    (r'^api/recent', 'pistelogs.views.recent_download'),
    # resort loading
    # this should be open only during resort data loading
    #(r'^api/depositresort', 'pistelogs.views.receive_resort'),
    (r'^api/queryresort', 'pistelogs.views.query_resort'),
    ######
    # TEST:
    ######
    (r'^test/raw_user_data/(.*)', 'pistelogs.views.test_raw_user_data'),
    (r'^test/polished_user_data/(.*)', 'pistelogs.views.test_polished_user_data'),    
    (r'^test/runs/(.*)', 'pistelogs.views.test_polished_user_runs'),      
    (r'^test/', 'pistelogs.views.test'),
)
