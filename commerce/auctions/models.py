from django.contrib.auth.models import AbstractUser
from django.db import models

# user model
class User(AbstractUser):
    watchItem = models.ManyToManyField("auctionListing", blank=True, related_name="watchingUsers")

    def __str__(self):
        return f"{self.id}: {self.username}"
 
# auction listing model
class auctionListing(models.Model): 
    #main item
    title = models.CharField(max_length=64)
    description = models.TextField()
    startingBid = models.DecimalField(max_digits=10, decimal_places=2)
    imgUrl = models.TextField()
    isActive = models.BooleanField(default=True)

    #category = models.CharField(max_length=64)#its own class
    category = models.ManyToManyField("categoryModel", blank=True, related_name="postedListings")

    #which user posted the listing
    fromUser = models.ManyToManyField("User", blank=True, related_name="postedListings")
    #topBid
    topBid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.title} for ${self.startingBid}"


# bid model
class bid(models.Model):
    #bid amount
    bidAmount = models.DecimalField(max_digits=10, decimal_places=2)
    #from which user
    fromUser = models.ManyToManyField("User", blank=True, related_name="bids")
    #for which item (listing)
    listing = models.ManyToManyField("auctionListing", blank=True, related_name="bids")

# comment model
class comment(models.Model):
    text = models.TextField()

    #who is the comment from
    fromUser = models.ManyToManyField("User", blank=True, related_name="comments")
    #what listing is the comment about
    listing = models.ManyToManyField("auctionListing", blank=True, related_name="comments")



class categoryModel(models.Model):
    name = models.CharField(max_length=64)





