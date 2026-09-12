from django.contrib import admin
from django.urls import include, path
from dealership.views import (
    home,
    about,
    contact,
    login_view,
    logout_view,
    dealer_reviews,
    all_reviews,
    post_review,
    review_success,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", home, name="home"),
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),

    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path(
        "dealers/<int:dealer_id>/reviews/",
        dealer_reviews,
        name="dealer_reviews"
    ),

    path(
        "reviews/",
        all_reviews,
        name="reviews"
    ),

    path(
        "dealers/<int:dealer_id>/review/",
        post_review,
        name="post_review"
    ),

    path(
        "review-success/",
        review_success,
        name="review_success"
    ),

    path("api/", include("cars.urls")),
]
