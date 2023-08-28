#imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required #decorator that can be used for some views functions
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *
from django import forms
from django.core.exceptions import ObjectDoesNotExist #when nothing satisfies objects.get(...=...) 


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
    category = forms.CharField(label = "category")

#helper functions\

def isOnWatchlist(user, listing): #checks if a given listing is on a user's watchlist
    #
    try:
        user.watchItem.get(pk=listing.pk)
        #if this works...
        return True
    except ObjectDoesNotExist:
        return False
    

def categoryExists(categoryName):
    try:
        categoryModel.objects.get(name=categoryName)

        return True
    except ObjectDoesNotExist:
        return False


#view functions

def index(request):
    return render(request, "auctions/index.html", {
        "listings": auctionListing.objects.all() 
    })

@login_required
def watchlist_view(request):
    #
    watchlist = request.user.watchItem.all()
    return render(request, "auctions/watchlist.html",{
        "watchlist": watchlist
    })

def categories_view(request):
    return render(request, "auctions/categories.html",{
        "categories": categoryModel.objects.all()
    })


def category_view(request, categoryName):

    category = categoryModel.objects.get(name=categoryName)
    listings = auctionListing.objects.filter(category=category)#get all the listings of the given category
    return render(request, "auctions/category.html", {
        "categoryName": categoryName,
        "listings": listings
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
            category = form.cleaned_data["category"]

            fromUser = request.user #user who posted the listing
            topBid = startingBid #initialize it as starting bid for now

            #add a new "listing" to auctionListing database (the django way lol)
            newListing = auctionListing(title=title, description=description, startingBid = startingBid, imgUrl = imgURL, topBid=topBid)
            newListing.save()#save here so u can add many-to-many attribute later
            #adding a value for a many to many attribute
            newListing.fromUser.add(fromUser)#this listing is form the user...above: fromUser=request.user

            #create category instance (if doesnt exist yet)
            if not categoryExists(category):
                #create and save new category instance
                newCategory = categoryModel(name=category)
                newCategory.save()

            #relate listing to category model
            newListing.category.add(categoryModel.objects.get(name=category))
            
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
    #get the listing instance, username, category
    listing = auctionListing.objects.get(pk=listingId)
    #have to do .all().first cuz its defined as a many-to-many attribute in the listing model
    username = listing.fromUser.all().first().username 
    category = listing.category.all().first().name

    
    if request.method == "POST":
        #get the btn message from te post request, act accordingly
        watchBtnMsg = request.POST.get("watchBtnMsg")

        if watchBtnMsg == "Add to Watchlist":
            #add
            request.user.watchItem.add(listing)
        else:
            #remove
            request.user.watchItem.remove(listing)

        #render the page like normal...

        #check if listing is on user watchlist
        if isOnWatchlist(request.user, listing):
            watchBtnMsg = "Remove from Watchlist"
        else:
            watchBtnMsg = "Add to Watchlist"

        #render page
        return render(request, "auctions/listingPage.html", {
            "posterUsername": username,
            "category": category,
            "listing": listing,
            "watchBtnMsg": watchBtnMsg
        })
    
    else: #GET request

        #check if listing is on user watchlist
        if isOnWatchlist(request.user, listing):
            watchBtnMsg = "Remove from Watchlist"
        else:
            watchBtnMsg = "Add to Watchlist"

        #render page
        return render(request, "auctions/listingPage.html", {
            "posterUsername": username,
            "category": category,
            "listing": listing,
            "watchBtnMsg": watchBtnMsg
        })