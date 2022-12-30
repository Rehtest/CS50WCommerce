from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auctions, Bids, Comments


def index(request):
    all_items = Auctions.objects.all()
    return render(request, "auctions/index.html", {
        "items": all_items
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

def add_listing(request):
    if request.method == "POST":
        item_title = request.POST["item_title"]
        item_description = request.POST["item_description"]
        item_price = request.POST["item_price"]
        item_image = request.POST["item_image"]
        item_category = request.POST["category"]
        item_owner = request.user
        save_listing = Auctions(item_title=item_title, item_description=item_description, item_price=item_price, item_image=item_image, item_category=item_category, item_owner=item_owner)
        save_listing.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/add.html")

def listing(request, title):
    item = Auctions.objects.get(item_title=title)
    confirm_owner = (request.user == item.item_owner)
    message = ""
    comments = Comments.objects.filter(item=item)
    try:
        your_bid = Bids.objects.get(item=item, bidder=request.user)
        print(your_bid.bidder)
    except:
        your_bid = ""
    try:
        watchlisted = request.user in item.watchlists.all()
    except:
        watchlisted = ""
    return render(request, "auctions/listing.html", {
                "title": title,
                "details": item,
                "watchlisted": watchlisted,
                "bid": your_bid,
                "owner":confirm_owner,
                "message": message,
                "comments": comments
        })

@login_required(login_url='/login')
def watchlist(request):
    if request.method == "POST":
        item = request.POST["item"]
        item_details = Auctions.objects.get(pk=item)
        user = request.user
        if request.POST["watchlistdata"] == "Add to watchlist":
            item_details.watchlists.add(user)
            return HttpResponseRedirect(reverse("listing", args=(item_details.item_title,)))
        else:
            item_details.watchlists.remove(user)
            return HttpResponseRedirect(reverse("listing", args=(item_details.item_title,)))
    user = request.user
    user_watchlist = user.watchlists.all()
    return render(request, "auctions/watchlist.html", {
        "watchlisted_items": user_watchlist
    })

@login_required(login_url='/login')
def bid(request):
    if request.method == "POST":
        bid = float(request.POST["bidvalue"])
        item = request.POST["item"]
        item_details = Auctions.objects.get(pk=item)
        user = request.user
        confirm_owner = (user == item_details.item_owner)
        try:
            your_bid = Bids.objects.get(item=item, bidder=user)
        except:
            your_bid = ""
        try:
            watchlisted = user in item.watchlists.all()
        except:
            watchlisted = ""
        if bid < item_details.item_price or bid < item_details.item_highbidprice:
            return render(request, "auctions/listing.html", {
                "title": item_details.item_title,
                "details": item_details,
                "watchlisted": watchlisted,
                "bid": your_bid,
                "owner":confirm_owner,
                "message": "Insufficient bid value"
        })
        else:
            item_details.item_highbidprice = bid
            item_details.save()
            new_bid = Bids.objects.filter(item_id=item, bidder_id=user)
            if new_bid.exists():
                Bids.objects.filter(item_id=item, bidder_id=user).update(bid=bid)
                your_bid = Bids.objects.get(item=item, bidder=user)
            else:
                new_bid = Bids(bidder=user, item=item_details, bid=bid)
                new_bid.save()
            return render(request, "auctions/listing.html", {
                "title": item_details.item_title,
                "details": item_details,
                "watchlisted": watchlisted,
                "bid": your_bid,
                "owner":confirm_owner,
                "message": "Bid updated."
        })           
            

def closeauction(request):
    if request.method == "POST":
        item = request.POST["item"]
        item_details = Auctions.objects.get(pk=item)
        item_details.item_active = 0
        item_details.save()
        return HttpResponseRedirect(reverse("index"))

def comment(request):
    if request.method == "POST":
        comment = request.POST["commentvalue"]
        user = request.user
        item = request.POST["item"]
        item_details = Auctions.objects.get(pk=item)
        new_comment = Comments(bidder=user, item=item_details, comment=comment)
        new_comment.save()
        return HttpResponseRedirect(reverse("listing", args=(item_details.item_title,)))

def categories(request):
    if request.method == "POST":
        choice_text = request.POST["category"]
        choice = choice_text.upper()[:2]
        print(choice)
        category = Auctions.objects.filter(item_category=choice)
        return render(request, "auctions/index.html", {
        "items": category
    })
    items = Auctions.objects.all()
    choices = items[0].CATEGORY_CHOICES
    choice_text = []
    for choice in choices:
        choice_text.append(choice[1])
    return render(request, "auctions/categories.html", {
        "items": items,
        "choices": choice_text
    })