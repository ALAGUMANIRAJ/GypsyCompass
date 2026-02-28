from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import traceback
import sys
from .ai_service import GeminiAIService

# Ensure console output handles Unicode (₹ symbol)
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except:
    pass
from .excel_service import save_user_data, get_client_ip, get_user_ip_location
from .models import TripRequest, ContactMessage


def _get_ai_service():
    """Create a fresh AI service instance each request so API key changes take effect immediately."""
    return GeminiAIService()


class GetRecommendationsView(APIView):
    """
    POST endpoint to get AI travel recommendations based on user preferences.
    Saves requests to the database for analytics.
    """

    def post(self, request):
        data = request.data

        # Validate required fields
        required_fields = ['name', 'budget', 'num_days', 'from_location']
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {'error': f'"{field}" is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Get user IP (for geographical context)
        ip_address = get_client_ip(request)
        ip_location = 'Unknown'
        try:
            ip_location = get_user_ip_location(ip_address)
        except Exception as e:
            print(f"IP location lookup failed (non-critical): {e}")

        # Parse destination styles safely
        raw_styles = data.get('destination_styles', [])
        if isinstance(raw_styles, str):
            raw_styles = [s.strip() for s in raw_styles.split(',') if s.strip()]
        elif not isinstance(raw_styles, list):
            raw_styles = []

        user_prefs = {
            'name': str(data.get('name', '')).strip(),
            'budget': float(data.get('budget', 50000)),
            'currency': str(data.get('currency', 'INR')).strip(),
            'travel_type': str(data.get('travel_type', 'solo')).strip(),
            'group_size': int(data.get('group_size', 1)),
            'travel_scope': str(data.get('travel_scope', 'within_country')).strip(),
            'num_days': int(data.get('num_days', 5)),
            'food_accommodation': str(data.get('food_accommodation', 'with')).strip(),
            'from_location': str(data.get('from_location', '')).strip(),
            'travel_medium': str(data.get('travel_medium', 'any')).strip(),
            'destination_styles': raw_styles,
        }

        print("\n--- New Trip Request ---")
        print(f"  Name: {user_prefs['name']} | From: {user_prefs['from_location']}")

        # Save to Excel (Local tracking - Ignored by Git)
        try:
            save_user_data(user_prefs, ip_address, ip_location)
            print("  Excel: saved OK")
        except Exception as e:
            print(f"  Excel: failed (non-critical) -> {e}")

        # Save to database (non-critical)
        try:
            TripRequest.objects.create(
                ip_address=ip_address,
                ip_location=ip_location,
                **user_prefs
            )
            print("  DB: saved OK")
        except Exception as e:
            print(f"  DB: failed (non-critical) -> {e}")

        # Get AI recommendations - ALWAYS returns a response
        try:
            ai_service = _get_ai_service()
            result = ai_service.get_travel_recommendations(user_prefs)

            if not result or not isinstance(result, dict):
                raise ValueError("AI service returned invalid response type")

            recs = result.get('recommendations', [])
            print(f"  Result: {len(recs)} recommendations returned")

            return Response({
                'success': True,
                'user_prefs': user_prefs,
                'ip_location': ip_location,
                'recommendations': recs,
                'ai_summary': result.get('ai_summary', ''),
            })

        except Exception as exc:
            print(f"  ERROR in AI service: {exc}")
            traceback.print_exc()
            return Response({
                'success': False,
                'error': str(exc),
                'recommendations': [],
                'ai_summary': 'Something went wrong generating recommendations. Please try again.',
                'user_prefs': user_prefs,
                'ip_location': ip_location,
            })


class GetDestinationDetailsView(APIView):
    """POST endpoint for detailed destination information."""

    def post(self, request):
        destination_name = request.data.get('destination_name', '').strip()
        user_prefs = request.data.get('user_prefs', {})

        if not destination_name:
            return Response(
                {'error': 'destination_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"\n--- Detail request: {destination_name} ---")

        try:
            ai_service = _get_ai_service()
            details = ai_service.get_destination_details(destination_name, user_prefs)
            return Response({'success': True, 'details': details})
        except Exception as exc:
            print(f"  Detail error: {exc}")
            traceback.print_exc()
            return Response({'success': False, 'error': str(exc), 'details': {}})


class LocationSuggestionsView(APIView):
    """GET endpoint for location autocomplete."""

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response({'suggestions': []})
        try:
            ai_service = _get_ai_service()
            suggestions = ai_service.get_location_suggestions(query)
            return Response({'suggestions': suggestions})
        except Exception as exc:
            print(f"Suggestion error: {exc}")
            return Response({'suggestions': []})


class ContactMessageView(APIView):
    """POST endpoint to receive contact form submissions."""

    def post(self, request):
        data = request.data
        name = str(data.get('name', '')).strip()
        email = str(data.get('email', '')).strip()
        message = str(data.get('message', '')).strip()

        # Validate required fields
        if not name or not email or not message:
            return Response(
                {'success': False, 'error': 'All fields (name, email, message) are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ContactMessage.objects.create(name=name, email=email, message=message)
            print(f"📧 New contact message from {name} ({email})")
            return Response({
                'success': True,
                'message': 'Your message has been sent successfully! We will get back to you within 24 hours.',
            })
        except Exception as exc:
            print(f"Contact form error: {exc}")
            return Response(
                {'success': False, 'error': 'Something went wrong. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """Health check endpoint."""

    def get(self, request):
        try:
            ai_service = _get_ai_service()
            return Response({
                'status': 'ok',
                'service': 'GypsyCompass API',
                'ai_available': ai_service.available,
                'ai_mode': 'Gemini AI (Real-time)' if ai_service.available else 'Smart Fallback (30+ destinations)',
                'version': '2.0.0',
            })
        except Exception as exc:
            return Response({'status': 'error', 'detail': str(exc)})
