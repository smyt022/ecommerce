#imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required #decorator that can be used for some views functions
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, auctionListing
from django import forms


#form classes to add new listings
class DecimalTwoPlacesField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['decimal_places'] = 2
        super().__init__(*args, **kwargs)

class newListingForm(forms.Form):
    title = forms.CharField(label="listing title")
    description = forms.CharField(widget=forms.Textarea, label = "discription")
    startingBid = DecimalTwoPlacesField()
    imgURL = forms.CharField(label="img url")
    catagory = forms.CharField(label = "catagory")

#helper functions


#view functions
def index(request):
    return render(request, "auctions/index.html", {
        "listings": auctionListing.objects.all() 
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

#only logged in users can create new listing 
@login_required
def newAuction(request):
    if request.method == "POST": #sent a form with info on new listing

        #add a new listing to SQL and go back to index
        form = newListingForm(request.POST)
        if form.is_valid():

            #extracting data
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            startingBid = form.cleaned_data["startingBid"]
            imgURL = form.cleaned_data["imgURL"]
            catagory = form.cleaned_data["imgURL"]

            fromUser = request.user #user who posted the listing
            topBid = startingBid #initialize it as starting bid for now

            #add a new "listing" to auctionListing database (the django way lol)
            newListing = auctionListing(title=title, description=description, startingBid = startingBid, imgUrl = imgURL, catagory = catagory, topBid=topBid)
            newListing.save()#save here so u can add many-to-many attribute later
            #adding a value for a many to many attribute
            newListing.fromUser.add(fromUser)#this listing is form the user...aabove: fromUser=request.user

            newListing.save()#save the many-to-many that was added
            #go back to index
            return HttpResponseRedirect(reverse("index"))

        else:#form is not valid, go back to same form page
            return HttpResponseRedirect(reverse("newAuction"))


    else:#it was a GET request
        return render(request, "auctions/new.html", {
            "form": newListingForm()
        })


def listingPage(request, listingId):
    #if ... get, post, etc

    #so far, this is just GET

    #get the listing instance
    listing = auctionListing.objects.get(pk=listingId)
    return render(request, "auctions/listingPage.html", {
        "title": listing.title,
        "description": listing.description,
        "imgUrl": listing.imgUrl,
        "topBid": listing.topBid
    })