from django.contrib import admin

from .models import User, auctionListing, bid, comment, categoryModel


# Register your models here.
admin.site.register(User)
admin.site.register(auctionListing)
admin.site.register(bid)
admin.site.register(comment)
admin.site.register(categoryModel)

