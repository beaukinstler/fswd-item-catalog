# Item catalog project


This is a sample project for Udacity's "Programming Foundations" course, and the Full Stack Web Dev nano-degree.

 In this project, I've created a Catalog app, in a very generic and basic way.  The intent is not to have a production ready application, but to demonstrate some of the core concepts of authentication, access control, and CRUD operations on a database.

## Getting Started


You'll need to have Python installed on your computer. Python 3.10 is the version this application 
has been updated to support. Python 2.7 would require using versions found in the git history.

I suggest using `pipenv` to create a [python environment](https://docs.pipenv.org/)
and the directions I give will assume you are using this.

Also, this app uses secrets stored in two json files. There are examples of these, file saved with this project, but should be replaced with your own.

TODO: #8  update this section, after getting oauth setup again
~~The first file, `client_secrets.json`, requires a Google OAuth API setup.  [See this Google documentation](https://developers.google.com/identity/protocols/OAuth2) to get setup and get your "client_secrets.json" file.~~

The next file is just a custom `secrets.json` file.  The only info stored in it is the secret key passed to the main flask `app` instance on first run. You can just remove the `.example` from the end of the suplied `secrets.json.example` file. If using in production, the value of "SUPER_SECRET_KEY" whould need to be kept secret.

One you have these json files ready, you can run the app.

## Usage

TODO: #7 update the zip file?
1. ~~Download and unzip the files in this [zip file](https://github.com/beaukinstler/fswd-item-catalog/archive/submition1.zip),~~ 
or clone with `git clone git@github.com:beaukinstler/fswd-item-catalog.git`
1. `cd` into the 'fswd-item-catalog' folder.
1. If you haven't installed `pip` on your machine, please do so.
1. If you haven't installed `pipenv`, type

        pip install pipenv

1. If you haven't yet created the _pipenv_, type:

        pipenv --python 3.10

1. Then, use the `Piplock` file to install the dependencies bu running:

        pipenv install
        
    _NOTE: If you don't want to use pipenv, and you wish to do this manually, read the `Pipfile and install the python dependencies listed`_

1. Now you should be close to ready. By default, this app runs on _http://localhost:5000_.  If you wish to change the port, or have a conflict, change the port at the end of the `main_app.py` file

1. Run the app, using this command:

        pipenv run python main_app.py

1. Open a web browser and type in _http://localhost:5000_, and be sure to change _5000_ if you customized the port.

## Logging in for the first time

__IMPORTANT__: The first time you visit the /login url, the application will create an "admin" account if one is not found in the database.  When it does, it sets the password to `password`.  You should first log in as `admin` and change the password.

When you navigate the `/login` page, you'll be asked authenticate, either with Google, or a username and password. 

After you setup the `admin` user, you can create another user using the "Create User" form.

## Creating users using OAuth
Another way to create a user is buy authenticating with OAuth, and specifically at this time, Google. The application will create a user in the database if no user matches the email address of your google account.

## JSON end points

There are a number of JSON endpoints available. After logging into the application, you can view the list by selecting the _JSON_ menu item.