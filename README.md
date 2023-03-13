# InterTech

InterTech is a web store which provides the following:

- Registration and authentication
- User profile
- Ability to change user's info and password
- Ability to form sales reports (only for managers and admins)
- Searching, filtering and sorting of commodities
- Ability to choose the number of commodities per page
- Ability to leave a comment
- Ability to buy a commodity (simulation of this process)

# Installation

To install the project follow these commands:

1. Navigate to the folder where you want to install the project and clone it by using `git clone url`, replace 'url' with the URL of this repository.
2. Create a virtual environment and activate it:
   - `py -m venv name`, replace 'name' with a name you like
   - `name\Scripts\activate.bat`
3. Install the dependencies by running `pip install -r requirements.txt`.
4. Change the directory to the "shop" and use `py manage.py runserver` to start the server.

Note: make sure to activate the virtual environment to run the Django project.
