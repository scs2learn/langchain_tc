import os
import requests
import json
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool # Essential for tool definition
from dotenv import load_dotenv

# Load environment variables for API keys
load_dotenv()

# --- Configuration (if applicable to tools) ---
# Ensure these are defined or imported here if tools directly use them
BASE_API_URL = "http://localhost:8000"
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

# --- Arithmetic Tools ---
@tool
def add(a: int, b: int) -> int:
    """Add two integers.
    Args:
        a: First integer
        b: Second integer
    """
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers.
    Args:
        a: First integer
        b: Second integer
    """
    return a * b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract the second integer from the first.
    Args:
        a: The integer to subtract from.
        b: The integer to subtract.
    """
    return a - b

@tool
def divide(a: int, b: int) -> float:
    """Divide the first integer by the second. Handles division by zero.
    Args:
        a: The dividend.
        b: The divisor.
    Returns:
        The result of the division as a float, or an error message if division by zero occurs.
    """
    if b == 0:
        return "Error: Cannot divide by zero."
    return float(a / b)

# --- REST API Tools for User Management ---
@tool
def get_all_users() -> str:
    """Fetches a list of all users from the user management system.
    Returns:
        A JSON string representation of the list of users.
    """
    try:
        response = requests.get(f"{BASE_API_URL}/get_users")
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error fetching all users: {e}"

@tool
def get_user_by_id(user_id: int) -> str:
    """Fetches details for a specific user by their user ID.
    Args:
        user_id: The integer ID of the user to retrieve.
    Returns:
        A JSON string representation of the user's data if found,
        or a descriptive error message if not found or an API error occurs.
    """
    try:
        url = f"{BASE_API_URL}/users/{user_id}"
        response_user_by_id = requests.get(url)
        response_user_by_id.raise_for_status()
        data = response_user_by_id.json()

        if not data:
            return f"User with ID {user_id} not found."
        
        return json.dumps(data)

    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 404:
            return f"Error: User with ID {user_id} not found on the server (404)."
        return f"HTTP error occurred while fetching user with ID {user_id}: {http_err}"
    except requests.exceptions.ConnectionError as conn_err:
        return f"Connection error: Could not connect to the user API. Is it running at {BASE_API_URL}? {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        return f"Timeout error while fetching user with ID {user_id}: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        return f"An unexpected request error occurred while fetching user with ID {user_id}: {req_err}"
    except json.JSONDecodeError:
        return f"Error: Failed to decode JSON response from user API for ID {user_id}. Raw response: {response_user_by_id.text}"

@tool
def add_new_user(
    user_id: int,
    first_name: str,
    last_name: str,
    dob: str, # YYYY-MM-DD format
    address_1: str,
    address_2: Optional[str] = "",
    city: str,
    state: str,
    zip_code: str, # Renamed from 'zip' to avoid Python keyword conflict
    phone: str,
    email: str
) -> str:
    """Adds a new user to the system. All fields are required except address_2.
    Args:
        user_id: Unique integer ID for the new user.
        first_name: User's first name.
        last_name: User's last name.
        dob: Date of birth in YYYY-MM-DD format.
        address_1: Primary address line.
        address_2: Secondary address line (optional).
        city: City of residence.
        state: State of residence (e.g., IL).
        zip_code: Zip code.
        phone: Phone number.
        email: Email address.
    Returns:
        A success message or an error message.
    """
    user_data = {
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "dob": dob,
        "address_1": address_1,
        "address_2": address_2,
        "city": city,
        "state": state,
        "zip": zip_code,
        "phone": phone,
        "email": email
    }
    try:
        response = requests.post(f"{BASE_API_URL}/add_user", json=user_data)
        response.raise_for_status()
        return f"User {first_name} {last_name} (ID: {user_id}) added successfully: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error adding user {first_name} {last_name}: {e}"

@tool
def delete_existing_user(user_id: int) -> str:
    """Deletes a user from the system by their user ID.
    Args:
        user_id: The integer ID of the user to delete.
    Returns:
        A success message or an error message.
    """
    try:
        response = requests.delete(f"{BASE_API_URL}/delete_user?user_id={user_id}")
        response.raise_for_status()
        return f"User with ID {user_id} deleted successfully: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error deleting user with ID {user_id}: {e}"

@tool
def update_existing_user(
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    dob: Optional[str] = None, # YYYY-MM-DD format
    address_1: Optional[str] = None,
    address_2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
) -> str:
    """Updates an existing user's information. Provide the user_id and any fields to update.
    Only the provided fields will be updated.
    Args:
        user_id: The integer ID of the user to update.
        first_name: (Optional) New first name.
        last_name: (Optional) New last name.
        dob: (Optional) New date of birth in YYYY-MM-DD format.
        address_1: (Optional) New primary address line.
        address_2: (Optional) New secondary address line.
        city: (Optional) New city.
        state: (Optional) New state.
        zip_code: (Optional) New zip code.
        phone: (Optional) New phone number.
        email: (Optional) New email address.
    Returns:
        A success message or an error message.
    """
    update_data = {"user_id": user_id}
    if first_name is not None: update_data["first_name"] = first_name
    if last_name is not None: update_data["last_name"] = last_name
    if dob is not None: update_data["dob"] = dob
    if address_1 is not None: update_data["address_1"] = address_1
    if address_2 is not None: update_data["address_2"] = address_2
    if city is not None: update_data["city"] = city
    if state is not None: update_data["state"] = state
    if zip_code is not None: update_data["zip"] = zip_code
    if phone is not None: update_data["phone"] = phone
    if email is not None: update_data["email"] = email

    try:
        response = requests.put(f"{BASE_API_URL}/update_user", json=update_data)
        response.raise_for_status()
        return f"User with ID {user_id} updated successfully: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error updating user with ID {user_id}: {e}"

# --- Weather API Tool ---
@tool
def get_current_weather(location: str, unit: Optional[str] = "metric") -> str:
    """Fetches the current weather conditions for a specified location.
    The location can be a city name, city name and country code (e.g., "London,GB"), or zip code.
    Args:
        location: The city name, city name and country code, or zip code (e.g., "Jacksonville", "London,GB", "90210").
        unit: (Optional) The unit of temperature. Can be "metric" (Celsius) or "imperial" (Fahrenheit). Defaults to "metric".
    Returns:
        A summary of the current weather, including temperature, description, humidity, and wind speed.
        Returns an error message if the location is not found or API fails.
    """
    if not OPENWEATHERMAP_API_KEY:
        return "Weather API key not configured. Please set the OPENWEATHERMAP_API_KEY environment variable."

    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}&units={unit}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if data.get("cod") == "404":
            return f"Weather information not found for {location}. Please check the location."

        main = data.get("main", {})
        weather_desc = data.get("weather", [{}])[0].get("description", "N/A")
        temp = main.get("temp", "N/A")
        humidity = main.get("humidity", "N/A")
        wind_speed = data.get("wind", {}).get("speed", "N/A")
        city_name = data.get("name", location)

        return (
            f"Current weather in {city_name}: "
            f"{weather_desc.capitalize()}. "
            f"Temperature: {temp}°{'C' if unit == 'metric' else 'F'}. "
            f"Humidity: {humidity}%. "
            f"Wind Speed: {wind_speed} {'m/s' if unit == 'metric' else 'mph'}."
        )

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather for {location}: {e}"
    except json.JSONDecodeError:
        return f"Error decoding JSON response from weather API for {location}."