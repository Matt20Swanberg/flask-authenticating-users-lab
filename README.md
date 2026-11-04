# Flask User Authentication Lab

## Overview

This project implements a basic user authentication system for a Flask-based blog application.

The application uses Flask sessions to maintain a user's login state across multiple HTTP requests. Users can log in using their username, remain authenticated after refreshing the page, and log out when finished.

The backend uses Flask, Flask-RESTful, SQLAlchemy, and Marshmallow, while the frontend uses React.

The primary objective is to demonstrate how session-based authentication works in a Flask application.

**Note:** This lab uses username-only authentication for educational purposes. Production applications should implement secure password verification and additional authentication protections.

## Technologies Used

- Python
- Flask
- Flask-RESTful
- Flask-SQLAlchemy
- Flask-Migrate
- Marshmallow
- SQLite
- React
- JavaScript
- Pipenv
- Pytest

## Features

### User Login

The application allows existing users to log in by submitting their username.

The login process:

- Retrieves the username from the incoming JSON request.
- Searches the database for a matching user.
- Stores the user's ID in the Flask session.
- Returns the serialized user information with HTTP `200 OK`.
- Returns HTTP `401 Unauthorized` when the username does not exist.

### User Logout

Users can terminate their authenticated session through the logout endpoint.

The application:

- Removes the user's ID from the Flask session.
- Safely handles logout requests when no user ID exists.
- Returns HTTP `204 No Content` after logout.

### Session Verification

The application provides an endpoint to determine whether a user is currently authenticated.

The session verification process:

- Retrieves the user ID from the Flask session.
- Searches the database for the corresponding user.
- Returns the serialized user information when the session is valid.
- Returns HTTP `401 Unauthorized` when no authenticated user is found.

### Session Persistence

Flask sessions allow users to remain logged in across multiple requests.

After a successful login, the user's ID is stored in the session:

```python
session['user_id'] = user.id
```

The browser retains a session cookie, allowing Flask to identify the user on subsequent requests, including after refreshing the page.

When the user logs out, their ID is removed:

```python
session.pop('user_id', None)
```

This prevents subsequent requests from identifying the user as authenticated.


## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Matt20Swanberg/flask-authenticating-users-lab
cd flask-authenticating-users-lab
```

### 2. Install Python Dependencies

```bash
pipenv install
pipenv shell
```

### 3. Install Frontend Dependencies

```bash
npm install --prefix client
```

### 4. Initialize the Database

Navigate to the server directory:

```bash
cd server
```

Apply the database migrations:

```bash
flask db upgrade
```

Seed the database:

```bash
python seed.py
```

### 5. Start the Flask Backend

From the `server` directory:

```bash
python app.py
```

The Flask API runs at:

```text
http://localhost:5555
```

### 6. Start the React Frontend

Open another terminal from the project's root directory:

```bash
npm start --prefix client
```

The React frontend uses the following proxy configuration in `client/package.json`:

```json
"proxy": "http://localhost:5555"
```

This allows frontend requests to communicate with the Flask backend and supports session cookies.

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/login` | Authenticates an existing user by username. |
| DELETE | `/logout` | Removes the authenticated user's ID from the session. |
| GET | `/check_session` | Retrieves the currently authenticated user. |

### Existing Blog Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/articles` | Retrieves the available blog articles. |
| GET | `/articles/<int:id>` | Retrieves an individual article by ID. |
| DELETE | `/clear` | Clears session-related values. |

## User Login

### POST `/login`

Authenticates a user using the username provided in the request body.

**Example Request:**

```http
POST /login
Content-Type: application/json
```

```json
{
  "username": "example_user"
}
```

### Successful Response: HTTP 200

Returns the serialized user information.

The response contains the fields defined by the application's `UserSchema`.

### Invalid Username: HTTP 401

If no matching user exists, the application returns:

```json
{
  "message": "Invalid Login"
}
```

### Database Query

The application retrieves the requested user using SQLAlchemy:

```python
user = User.query.filter(
    User.username == request.get_json()['username']
).first()
```

If a matching user exists, their ID is stored in the session:

```python
if user:
    session['user_id'] = user.id
    return UserSchema().dump(user), 200
```

This allows subsequent requests to identify the authenticated user.

## User Logout

### DELETE `/logout`

Terminates the current user's login session.

### Successful Response: HTTP 204

Returns no response content.

### Session Management

The application removes the user ID using:

```python
session.pop('user_id', None)
```

The second argument prevents a `KeyError` if the session does not contain a `user_id` key.

This allows logout requests to complete safely even when the user is already logged out.

## Session Verification

### GET `/check_session`

Checks whether the current Flask session belongs to an authenticated user.

### Successful Response: HTTP 200

Returns the serialized user information when the session contains a valid user ID.

### Unauthorized Response: HTTP 401

Returns an empty JSON object when no authenticated user is found.

```json
{}
```

### Database Query

The application retrieves the user associated with the current session:

```python
user = User.query.filter(
    User.id == session.get('user_id')
).first()
```

If the user exists:

```python
if user:
    return UserSchema().dump(user), 200
```

Otherwise:

```python
return {}, 401
```

Using `session.get('user_id')` prevents a `KeyError` when the session does not contain a user ID.

## Authentication Workflow

The authentication process follows these steps:

1. A user opens the React application.
2. The user enters their username into the login form.
3. The frontend sends a POST request to `/login`.
4. Flask retrieves the username from the request body.
5. SQLAlchemy searches the database for the matching user.
6. If the user exists, Flask stores their ID in `session['user_id']`.
7. Marshmallow serializes the user information.
8. Flask returns the serialized user with HTTP `200 OK`.
9. The browser retains the session cookie.
10. Subsequent requests to `/check_session` use the session to identify the logged-in user.
11. Refreshing the browser does not automatically terminate the login session.
12. When the user logs out, a DELETE request to `/logout` removes their ID from the session.
13. Subsequent session checks return HTTP `401 Unauthorized`.

## Testing

Automated tests are provided to verify the authentication functionality.

From the `server` directory, run:

```bash
pytest -x
```

The `-x` flag stops execution after the first failed test.

To run the complete test suite:

```bash
pytest
```

To display individual test results:

```bash
pytest -v
```

### Authentication Test Coverage

| Test | Description |
|---|---|
| `test_logs_user_in` | Verifies that login retrieves a user and stores their ID in the session. |
| `test_logs_user_out` | Verifies that logout removes the authenticated user's session ID. |
| `test_checks_session` | Verifies that session checking returns the authenticated user. |

### Additional Validation

The login endpoint includes handling for usernames that do not exist in the database.

This is an additional improvement beyond the primary login requirements.

### Manual Testing

The application can also be tested through the React frontend.

1. Start the Flask backend and React frontend.
2. Open the application in the browser.
3. Log in using a username from the seeded database.
4. Confirm that the application recognizes the authenticated user.
5. Refresh the browser and verify that the login session persists.
6. Log out of the application.
7. Verify that the user is no longer authenticated.

## Screenshots

### Automated Test Suite Results

The following screenshot demonstrates the automated test results for the authentication functionality.

![Test Suite Results](screenshot/test_suite.png)

## Code Structure and Design

The application uses Flask-RESTful `Resource` classes to organize API functionality.

### Login Resource

The `Login` resource handles user authentication through the `post()` method.

Its responsibilities include:

- Retrieving the username from the incoming JSON request.
- Querying the database for the matching user.
- Storing the authenticated user's ID in the Flask session.
- Serializing the user information.
- Returning the appropriate HTTP response.

### Logout Resource

The `Logout` resource handles user logout through the `delete()` method.

Its responsibilities include:

- Removing the authenticated user's ID from the session.
- Safely handling missing session values.
- Returning HTTP `204 No Content`.

### CheckSession Resource

The `CheckSession` resource verifies the current authentication state through the `get()` method.

Its responsibilities include:

- Retrieving the user ID from the Flask session.
- Querying the database for the corresponding user.
- Returning the serialized user information when authenticated.
- Returning HTTP `401 Unauthorized` when no valid user exists.

### Session Management

Flask sessions maintain the user's authentication state across multiple requests.

The application uses:

```python
session['user_id'] = user.id
```

to store the authenticated user ID.

It uses:

```python
session.get('user_id')
```

to retrieve the current user ID safely.

Finally:

```python
session.pop('user_id', None)
```

removes the session value when the user logs out.

### Serialization

Marshmallow schemas convert SQLAlchemy model instances into JSON-compatible data.

For example:

```python
UserSchema().dump(user)
```

This separates database operations from API response formatting.

## HTTP Response Codes

| Status Code | Meaning | Usage |
|---|---|---|
| 200 | OK | Successful login or session verification |
| 204 | No Content | Successful logout |
| 401 | Unauthorized | Invalid username or unauthenticated session |
| 404 | Not Found | Requested endpoint does not exist |

## Security Considerations

This project demonstrates basic authentication concepts and is intended for educational use.

The application authenticates users using their usernames without requiring passwords.

In a production environment, additional security measures would be necessary, including:

- Secure password hashing and verification.
- Protection against brute-force login attempts.
- Secure session cookie configuration.
- HTTPS for encrypted communication.
- Session expiration and invalidation.
- CSRF protection where appropriate.
- Secure management of application secrets.


## Conclusion

This lab demonstrates how Flask sessions can be used to authenticate users and maintain their login state across multiple HTTP requests.

By implementing the `Login`, `Logout`, and `CheckSession` resources, the application can identify authenticated users, preserve login sessions across browser refreshes, and terminate sessions when users log out.

The project reinforces important backend development concepts, including RESTful API design, SQLAlchemy database queries, Marshmallow serialization, HTTP response codes, and Flask session management.

It also establishes a foundation for implementing authorization and protecting application resources in future projects.


## Author

Created by Matthew Swanberg as part of Course 10 Module 2 (Lab: Authentication Users)
