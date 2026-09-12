from django.urls import path
from .views import (
    dealer_list,
    dealer_detail,
    dealers_by_state,
    create_review,
)

urlpatterns = [
    path("dealers/", dealer_list, name="dealer_list"),
    path("dealers/<int:dealer_id>/", dealer_detail, name="dealer_detail"),
    path("dealers/state/<str:state>/", dealers_by_state, name="dealers_by_state"),
    path("dealers/<int:dealer_id>/reviews/", create_review, name="create_review"),
]
