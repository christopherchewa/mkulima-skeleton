"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from accounts import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^login', views.login_view),
    #url(r'^logout/', views.logout_view),
    url(r'^registeradmin/', views.admin_register_view),
    url(r'^(?P<pk>\d+)/addmember/$', views.add_sacco_members_view),
    url(r'^registermkulima/', views.add_mkulima_view),
    url(r'^registercustomer/', views.add_customer_view),
    url(r'^', include('accounts.urls')),
]



if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)