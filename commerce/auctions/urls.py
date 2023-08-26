from django.urls import path

from . import views
 
urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.newAuction, name="newAuction"),
    path("listing/<str:listingId>", views.listingPage, name="listingPage")
]
