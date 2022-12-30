from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auctions(models.Model):
    #If changing this, make sure to change the select options in "auctions/add.html" as well.
    FASHION = "FA"
    TOYS = "TO"
    ELECTRONICS = "EL"
    HOME = "HO"
    ANTIQUE = "AN"
    FOOD = "FO"
    VEHICLE = "VE"
    CATEGORY_CHOICES = [
        (FASHION, "Fashion"),
        (TOYS, "Toys"),
        (ELECTRONICS, "Electronics"),
        (HOME, "Home"),
        (ANTIQUE, "Antique"),
        (FOOD, "Food"),
        (VEHICLE, "Vehicles"),
    ]
    
    item_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    item_title = models.CharField(max_length=64)
    item_description = models.CharField(max_length=255)
    item_price = models.FloatField(default=0)
    item_highbidprice = models.FloatField(default=0)
    item_image = models.CharField(max_length=255)
    item_category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=HOME)
    item_active = models.IntegerField(default=1)
    watchlists = models.ManyToManyField(User, blank=True, related_name="watchlists")

    class Meta:
        verbose_name_plural = "Auctions"

    def __str__(self):
        return f"{self.item_title}: {self.item_description} {self.watchlists}"

class Bids(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidders")
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="items")
    bid = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "Bids"

class Comments(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenters")
    item = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name="bid_item", default=0)
    comment = models.CharField(max_length=255)