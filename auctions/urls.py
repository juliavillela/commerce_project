from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listing/<str:listing_id>", views.listing, name="listing"),
    path("category/<str:name>", views.category, name="category"),

    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("dashboard", views.dashboard, name="dashboard"),
    path("create", views.create, name="create"),
    path("edit/<str:listing_id>", views.edit, name="edit"),
    path("watchlist", views.watchlist, name='watchlist'),
    path("my_listings", views.my_listings, name='my_listings')
]
