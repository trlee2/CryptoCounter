from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.market, name='market'),
    path('market', views.market, name='market'),
    path('ico', views.ico, name='ico'),
    path('socialtrends', views.socialTrends, name='socialtrends'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('login', views.login, name='login'),
    path('logout', auth_views.logout, {'next_page': 'market'}, name='logout'),
    path('register', views.register, name='register'),
    path('header.html', views.header, name='header'),
    path('footer.html', views.footer, name='footer'),
]
