from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.add_listing, name="add"),
    path("listing/<str:title>", views.listing, name="listing"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("close", views.closeauction, name="close"),
    path("comment", views.comment, name="comment"),
    path("categories", views.categories, name="categories")
]
