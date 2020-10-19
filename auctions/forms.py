from django.forms import ModelForm, Textarea, TextInput

from .models import Listing, Comment, Bid

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ('category','name', 'description', 'img_url', 'external_link')
        widgets = {
            'name': TextInput(attrs={"placeholder": "a short and descriptive title works best :)"}),
            'description': Textarea(attrs={"placeholder": "tell us about your product!"}),
            'img_url': TextInput(attrs={"placeholder":"paste the link to an image of your product"}),
            'external_link': TextInput(attrs={"placeholder": "you can add a link to your own website here"})
            }
        labels = {
            "name": "Listing title:",
            "img_url":"Link to image:",
            "external_link":"external link:"
        }
        help_text = {
            "name": "a short and descriptive text works best.",
            "description": "Give us more details about your product.",
            "img_url":"select an image and paste it's addrees here!",
        }

# class CommentForm(ModelForm):
#     class Meta:
#         model = Comment
#         fields = ('text',)

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ('value',)
        labels = {
            "value": "starting bid:",
}
