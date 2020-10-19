from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return self.username

    #returns listings user has bidded on
    def bidded_on(self):
        bids = self.bids.all()
        listings = []
        for bid in bids:
            if bid.listing not in listings and bid.listing.user != self:
                listings.append(bid.listing)
        return listings


class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=500)
    active = models.BooleanField(default=True)
    img_url = models.URLField(blank=True, null=True, max_length=500, default="")
    external_link= models.URLField(blank=True, null=True, default="", max_length=500)
    watched = models.ManyToManyField(User, related_name="watchlist", blank=True)
    created_at = models.DateTimeField(auto_now_add = True, auto_now = False)
    updated_at = models.DateTimeField(auto_now_add = False, auto_now = True)

    PLANTS = 'PLA'
    COMPLEMENTS ='CMP'
    ACCESSORIES = 'ACC'
    HANDMADE = 'HMD'
    CONTAINERS ='CNT'

    CATEGORY_CHOICES = [
        (PLANTS, 'plants and seeds'),
        (HANDMADE, 'Handmade plant art'),
        (CONTAINERS, 'pots, vases and jars')
    ]
    category = models.CharField(
        max_length=3,
        choices=CATEGORY_CHOICES,
        default=PLANTS,
    )

    def __str__(self):
        return f"{self.pk}: {self.name} - by {self.user.username}"

    #returns either listing's image, or path to noimg file.
    def img(self):
        if self.img_url:
            return self.img_url
        else:
            return "/static/auctions/imgs/noimg.png"

    #returns latest bid object
    def highest_bid(self):
        highest = self.bids.order_by('-created_at').first()
        return highest


    #returns float value of next minimum bid
    def next_bid(self):
        min_new_bid = float(self.highest_bid().value) + 0.50
        return min_new_bid

    #returns difference between min-bid and current price as float
    def price_increase(self):
        current = self.highest_bid()
        min_bid = self.bids.get(user=self.user)
        increase = current.value - min_bid.value
        return float(increase)

    #returns list of categories
    def categories(self):
        return self.CATEGORY_CHOICES

    #sets active to false
    def close(self):
        self.active = False
        self.save()

    #returns the date of the most recent activity in listing
    def latest_activity(self):
        latest_activity = [self.updated_at]
        latest_activity.append(self.highest_bid().created_at)
        latest_comment = self.listing_comments.order_by('-created_at').first()
        if latest_comment:
            latest_activity.append(latest_comment.created_at)
        latest_activity.sort(reverse=True)
        return latest_activity[0]


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing,
        on_delete=models.CASCADE,
        related_name="listing_comments")
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add = True, auto_now = False)
    reply_to = models.ForeignKey('self',
        on_delete= models.CASCADE,
        blank=True,
        null=True,
        related_name="replies")

    def __str__(self):
        return self.text

    #sets reply_to to comment
    def reply(self, comment):
        self.reply_to = comment
        self.listing.latest_activity()
        self.save()


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add = True, auto_now = False)

    def __str__(self):
        return f"${self.value}: {self.user} on {self.listing}"
