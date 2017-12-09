"""DB_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from bookstore import views as bs_views

urlpatterns = [
    url(r'^$',bs_views.login,name = 'login'),
    url(r'^login/$',bs_views.login,name = 'login'),
    url(r'^register/$',bs_views.register,name = 'register'),
    url(r'^user_info/$',bs_views.user_info_float,name = 'order'),
    url(r'^order/$',bs_views.order,name = 'order'),
    url(r'^my_order_history/$',bs_views.order_history,name = 'order_history'),
    url(r'^comment/$', bs_views.comment, name='book_comments'),
    url(r'^my_comment_history/$', bs_views.my_comment, name='my_comments'),
    url(r'^view_all_orders/$', bs_views.all_order_history, name='view_all_orders'),
    url(r'^create_book/$', bs_views.create_books, name='create_book'),
    url(r'^add_book/$', bs_views.add_book, name='add_book'),
    url(r'^overview/$', bs_views.admin_panel, name='admin_panel'),
]
