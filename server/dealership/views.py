from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from cars.models import Dealer, Review
from textblob import TextBlob


def home(request):
    dealers = Dealer.objects.all().order_by("dealer_id")
    return render(request, "home.html", {"dealers": dealers})


def about(request):
    with open("frontend/static/About.html", encoding="utf-8") as f:
        return HttpResponse(f.read())


def contact(request):
    with open("frontend/static/Contact.html", encoding="utf-8") as f:
        return HttpResponse(f.read())


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            next_url = request.GET.get("next") or request.POST.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")

        from django.contrib import messages
        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


def dealer_reviews(request, dealer_id):
    dealer = get_object_or_404(Dealer, dealer_id=dealer_id)
    reviews = Review.objects.filter(dealer=dealer).order_by("-created_at")

    return render(
        request,
        "dealer_reviews.html",
        {
            "dealer": dealer,
            "reviews": reviews,
        }
    )


def all_reviews(request):
    reviews = Review.objects.select_related(
        "dealer",
        "user"
    ).order_by("-created_at")

    return render(
        request,
        "reviews.html",
        {
            "reviews": reviews,
        }
    )


def post_review(request, dealer_id):
    dealer = get_object_or_404(Dealer, dealer_id=dealer_id)

    if not request.user.is_authenticated:
        return redirect(
            f"/login/?next=/dealers/{dealer_id}/review/"
        )

    if request.method == "POST":
        review_text = request.POST.get("review", "").strip()
        rating = request.POST.get("rating", "5")

        if not review_text:
            return render(
                request,
                "post_review.html",
                {
                    "dealer": dealer,
                    "error": "Review cannot be empty.",
                }
            )

        try:
            rating = int(rating)
        except ValueError:
            rating = 5

        if rating < 1 or rating > 5:
            rating = 5

        polarity = TextBlob(review_text).sentiment.polarity

        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        new_review = Review.objects.create(
            dealer=dealer,
            user=request.user,
            review=review_text,
            rating=rating,
            sentiment=sentiment,
        )

        return redirect(
            f"/review-success/?review_id={new_review.id}"
        )

    return render(
        request,
        "post_review.html",
        {
            "dealer": dealer,
        }
    )


def review_success(request):
    review_id = request.GET.get("review_id")

    review = get_object_or_404(
        Review.objects.select_related("dealer", "user"),
        id=review_id
    )

    return render(
        request,
        "review_success.html",
        {
            "review": review,
        }
    )
