activities =[]

def get_activities(user):
    activities.clear()
    #in user listings
    for listing in user.listings.all():
        #check for new comments
        comments(user, listing)
        #check for new bids
        bids(user, listing)
    #check for replies to user comments
    replies(user)
    #check for won bids
    won(user)
    activities.sort(key= lambda activity: activity["date"], reverse=True)
    return activities

#gets all replies to user comments
def replies(user):
    for comment in user.comments.all():
        for reply in comment.replies.all():
            if reply.user != user:
                note=f"{span(reply.user)} has replied to your comment in {span(reply.listing.name)}"
                activities.append({
                    "date": reply.created_at,
                    "note": note,
                    "href": reply.listing.id})

#gets all comments in user's listings
def comments(user, listing):
    for comment in listing.listing_comments.all():
        if comment.user != user:
            note = f"{span(comment.user)} has commented on your listing {span(listing.name)}"
            activities.append({"date": comment.created_at, "note": note, "href": listing.id})

#gets all bids in user's listings
def bids(user, listing):
    for bid in listing.bids.all():
        if bid.user != user:
            note = f"{span(bid.listing.name)} has received a new bid!"
            activities.append({"date": bid.created_at, "note": note, "href": listing.id})

#gets all wins in user's bids
def won(user):
    listings = user.bidded_on()
    for listing in listings:
        if not listing.active and listing.highest_bid().user is not user:
            note = f"CONGRATULATIONS! you are the winner for listing {span(listing.name)}"
            activities.append({"date": listing.updated_at, "note": note, "href": listing.id})

#formats as html span
def span(string):
    return f"<span = class='green-bold'>{string}</span>"
