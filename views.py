import json
import logging
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    """
    Handle sign-in requests with username and password.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    username = data.get('userName', '')
    password = data.get('password', '')

    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    """
    Handle sign-out requests and clear session.
    """
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)


# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    """
    Handle user sign-up requests, validate credentials, and maintain session.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    username = data.get('userName', '').strip()
    password = data.get('password', '')
    first_name = data.get('firstName', '').strip()
    last_name = data.get('lastName', '').strip()
    email = data.get('email', '').strip()

    if not username or not password:
        return JsonResponse({"error": "Username and password are required"}, status=400)

    username_exist = User.objects.filter(username=username).exists()

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    else:
        return JsonResponse({"userName": username, "error": "Already Registered"})


def get_cars(request):
    """
    Return all CarModels and their associated CarMake.
    Seed initial data if database is currently empty.
    """
    count = CarMake.objects.count()
    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make').all()
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })
    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    """
    Proxy request to get all dealerships or dealerships by state.
    """
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"

    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships if dealerships is not None else []})


def get_dealer_details(request, dealer_id):
    """
    Proxy request to get dealer details by ID.
    """
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership if dealership is not None else []})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_reviews(request, dealer_id):
    """
    Proxy request to get reviews for a dealer and enrich them with sentiment analysis.
    """
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)
        reviews_list = reviews if reviews is not None else []

        for review_detail in reviews_list:
            review_text = review_detail.get('review')
            if review_text:
                response = analyze_review_sentiments(review_text)
                if response and 'sentiment' in response:
                    review_detail['sentiment'] = response['sentiment']
                else:
                    review_detail['sentiment'] = 'neutral'
            else:
                review_detail['sentiment'] = 'neutral'

        return JsonResponse({"status": 200, "reviews": reviews_list})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


@csrf_exempt
def add_review(request):
    """
    Submit a customer review to the backend service.
    """
    if request.method != "POST":
        return JsonResponse({"status": 405, "message": "Method Not Allowed"}, status=405)

    if not request.user.is_anonymous:
        try:
            data = json.loads(request.body)
            response = post_review(data)
            if response is not None:
                return JsonResponse({"status": 200})
            else:
                return JsonResponse({"status": 401, "message": "Error in posting review"})
        except Exception as err:
            logger.error(f"Error in posting review: {err}")
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
