from django.urls import path
from .views import (
    GetRecommendationsView,
    GetDestinationDetailsView,
    LocationSuggestionsView,
    ContactMessageView,
    HealthCheckView,
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('recommendations/', GetRecommendationsView.as_view(), name='get-recommendations'),
    path('destination-details/', GetDestinationDetailsView.as_view(), name='destination-details'),
    path('location-suggestions/', LocationSuggestionsView.as_view(), name='location-suggestions'),
    path('contact/', ContactMessageView.as_view(), name='contact-message'),
]
