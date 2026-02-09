# Flask Blackjack (MVP)

## Project Overview
A web-based implementation of Blackjack built with Python(Flask)
This project is about transition from a Console Application to a Web Application.

## Tech Stack
* **Backend:** Python 3.12, Flask
* **Frontend:** HTML5, CSS(Jinja2, Templates)
* **State Management:** Flask Sessions(Cookie-based)
* **Deployment:** PythonAnywhere (Linux/WSGI)

## Architecture
The application uses a standard MVC (Model-View-Controller) pattern:
1.  **Models:** `BJ_classes.py` (Card, Deck, Hand objects)
2.  **View:** `templates/game.html` (The user interface)
3.  **Controller:** `app.py` (Routes that handle game logic and session management)
