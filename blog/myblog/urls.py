from . import views
from django.urls import path
from myblog.views import (SignUpView, SignInView, FeedBackView, SuccessView,
                          SearchResultView, PostDetailView)
from django.contrib.auth.views import LogoutView
from django.conf import settings

app_name = 'myblog'

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/<slug>/', PostDetailView.as_view(), name='post_detail'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('signout/', LogoutView.as_view(),
         {'next_page': settings.LOGOUT_REDIRECT_URL}, name='signout',),
    path('contact/', FeedBackView.as_view(), name='contact'),
    path('contact/success/', SuccessView.as_view(), name='success'),
    path('search/', SearchResultView.as_view(), name='search_results'),
    path('tag/<slug:slug>/', views.tag, name='tag'),
]
