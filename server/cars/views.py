from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import Dealer, Review
from textblob import TextBlob
import json


def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"


def dealer_list(request):
    dealers = Dealer.objects.all().order_by("dealer_id")

    data = []
    for dealer in dealers:
        data.append({
            "id": dealer.dealer_id,
            "name": dealer.name,
            "address": dealer.address,
            "city": dealer.city,
            "state": dealer.state,
            "zip": dealer.zip,
        })

    return JsonResponse(data, safe=False)


def dealer_detail(request, dealer_id):
    dealer = get_object_or_404(Dealer, dealer_id=dealer_id)
    reviews = Review.objects.filter(dealer=dealer).order_by("-created_at")

    data = {
        "id": dealer.dealer_id,
        "name": dealer.name,
        "address": dealer.address,
        "city": dealer.city,
        "state": dealer.state,
        "zip": dealer.zip,
        "reviews": [
            {
                "id": review.id,
                "user": review.user.username,
                "review": review.review,
                "rating": review.rating,
                "sentiment": review.sentiment,
                "created_at": review.created_at.isoformat(),
            }
            for review in reviews
        ],
    }

    return JsonResponse(data)


def dealers_by_state(request, state):
    dealers = Dealer.objects.filter(
        state__iexact=state
    ).order_by("dealer_id")

    data = [
        {
            "id": dealer.dealer_id,
            "name": dealer.name,
            "address": dealer.address,
            "city": dealer.city,
            "state": dealer.state,
            "zip": dealer.zip,
        }
        for dealer in dealers
    ]

    return JsonResponse(data, safe=False)


@csrf_exempt
def create_review(request, dealer_id):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405
        )

    dealer = get_object_or_404(Dealer, dealer_id=dealer_id)

    try:
        body = json.loads(request.body)

        username = body.get("username")
        review_text = body.get("review")
        rating = int(body.get("rating", 5))

        if not username or not review_text:
            return JsonResponse(
                {"error": "username and review are required."},
                status=400
            )

        if rating < 1 or rating > 5:
            return JsonResponse(
                {"error": "rating must be between 1 and 5."},
                status=400
            )

        user = get_object_or_404(User, username=username)

        sentiment = get_sentiment(review_text)

        review = Review.objects.create(
            dealer=dealer,
            user=user,
            review=review_text,
            rating=rating,
            sentiment=sentiment
        )

        return JsonResponse({
            "message": "Review created successfully.",
            "review": {
                "id": review.id,
                "dealer": dealer.name,
                "user": user.username,
                "review": review.review,
                "rating": review.rating,
                "sentiment": review.sentiment,
                "created_at": review.created_at.isoformat(),
            }
        }, status=201)

    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse(
            {"error": "Invalid request data."},
            status=400
        )
