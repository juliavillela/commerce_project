from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Comment, Bid
from.forms import ListingForm, BidForm
from.notifications import get_activities

def index(request):
    #get all active listings, than sort by recent activity
    active_listings = Listing.objects.filter(active=True)
    active_listings = sorted(active_listings,
        key=lambda this_listing: this_listing.latest_activity(),
        reverse=True)
    return render(request, "auctions/index.html", {
        'listings':active_listings,
        'page_title': "active listings"
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


@login_required
def create(request):
    if request.method == "POST":
        #build listing object from current user and form
        new_listing = Listing(user = request.user)
        new_listing = ListingForm(request.POST, instance=new_listing)

        if new_listing.is_valid():
            #save listing than save minimum bid from bidform
            this_listing = new_listing.save()
            min_bid = Bid(user=request.user, listing=this_listing)
            min_bid = BidForm(request.POST, instance=min_bid)
            if min_bid.is_valid():
                min_bid.save()

            #return new listing page
            return HttpResponseRedirect(reverse("listing", kwargs={'listing_id': this_listing.pk}))

        else:
            #return form containing input and message
            messages.warning(request,
                "something went wrong and your listing could not be saved. please try again.")
            return render (request, "auctions/create_listing.html", {
            "listing_form": new_listing,
            "bid_form": BidForm()
        })

    else:
        #get listing and bid form
        listing_form = ListingForm()
        bid_form = BidForm()
        return render(request, "auctions/create_listing.html", {
            "listing_form": listing_form,
            "bid_form": bid_form
        })

@login_required
def edit(request, listing_id):
    #gets listing object from id
    this_listing = Listing.objects.get(pk=int(listing_id))
    if request.method == "POST":
        #save changes made to listing from
        form = ListingForm(request.POST, instance=this_listing)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse('listing', kwargs={
            'listing_id':this_listing.id
        }))
    else:
        #display form filled with listing data
        form = ListingForm(instance=this_listing)
        return render(request, "auctions/edit.html", {
            "form": form,
            "listing": this_listing
        })


def listing(request, listing_id):

    if request.method == "POST":
        #get post action
        action = request.POST.get("action")
        this_listing = Listing.objects.get(pk=listing_id)

        #save comment instance
        if action == "comment":
            #create new comment from form and save if valid.
            text= request.POST.get("text")
            reply_to = request.POST.get("reply_to")
            new_comment = Comment(
                user = request.user,
                listing = this_listing,
                text = text)
            new_comment.save()
            #if comment is reply, add reply field data
            if reply_to != "":
                new_comment.reply(Comment.objects.get(pk=int(reply_to)))

        #close listing
        elif action == "close":
            #close bid
            this_listing.close()
            messages.success(request, "listing has been closed.")

        #add bid
        else:
            bid_value = request.POST.get("value")
            new_bid = Bid(user = request.user, listing=this_listing, value= bid_value)
            try:
                new_bid.save()
                messages.success(request, "Bid saved!")
            except IntegrityError:
                messages.error(request, "there was a problem with your bid. please try again.")

        #reload listing page
        return HttpResponseRedirect(reverse("listing", kwargs={
        'listing_id':listing_id
        }))

    else:
        #get listing object fom listing_id
        try:
            this_listing = Listing.objects.get(pk=listing_id)
        except ObjectDoesNotExist:
            return HttpResponse("listing does not exist")
        bid = BidForm()
        comment = "commentForm"
        return render(request, "auctions/listing.html", {
            'listing': this_listing,
            'comment_form':comment,
            'bid_form': bid
            })

@login_required
def my_listings(request):
    listings = Listing.objects.filter(user = request.user)
    return render(request, "auctions/index.html", {
            "listings":listings,
            "page_title": "my listings"
        })


def category(request, name):
    #gets a list of categories names
    categories = Listing.objects.first().categories()
    #/list returns categories page
    if name == "list":
        return render(request, "auctions/categories.html", {
            "categories_list": categories,
        })
    else:
        #filter all listings in this category and return
        listings = Listing.objects.filter(category=name, active=True)
        categories = listings[0].categories()
        category_name =""
        for cat in categories:
            if cat[0] == name:
                category_name = cat[1]

        return render(request, "auctions/index.html", {
            "listings":listings,
            "page_title": category_name
        })


@login_required
def watchlist(request):
    if request.method == "POST":
        #gets listing object
        listing_id = request.POST.get("listing_id")
        this_listing = Listing.objects.get(pk = listing_id)
        action = request.POST.get("action")
        if action == "add":
            #adds to watchlist
            request.user.watchlist.add(this_listing)
            messages.success(request, f"{this_listing.name} has been added to your watchlist")
        else:
            #removes from watchlist
            request.user.watchlist.remove(this_listing)
            messages.success(request, f"{this_listing.name} has been removed from your watchlist")

        return HttpResponseRedirect(reverse('listing', kwargs={
            'listing_id':this_listing.id
        }))
    #request GET renders watchlist page.
    return render(request, "auctions/index.html",  {
        "listings": request.user.watchlist.all(),
        "page_title": "My watchlist"
    })


@login_required
def dashboard(request):
    #gets notification data
    notifications=get_activities(request.user)

    #gets watchlist and my lists sorted by recent activity
    recent_watchlist = request.user.watchlist.all()
    watch = sorted(recent_watchlist,
        key=lambda this_listing: this_listing.latest_activity(),
        reverse=True)
    recent_my_lists = request.user.listings.all()
    mine = sorted(recent_my_lists,
        key=lambda this_listing: this_listing.latest_activity(),
        reverse=True)

    #returns all notificatios + 4 most recent watches and lists
    return render(request, "auctions/dashboard.html", {
        "notifications":notifications,
        "watchlist": watch[:4],
        "my_listings": mine[:4]
        })
