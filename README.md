# Weather Telegram Bot

 The bot helps to find out the current weather in the specified city.
 It can also send a daily weather report for the whole day
 at a time specified by the user. 
 There is a possibility to receive notifications of upcoming events 
 user chose.
 For instance, the user notification of an impending hurricane
 this week.


# Installation

* Open the repository in development environment.

`git clone "https://github.com/shadeshade/weather_bot.git"`

`cd weather_bot`

* Install requirements

 `$ pip install requirements.txt`

# Deploying on Heroku

Set `DEBUG = False` in settings.py

Create `credentials.py` in the root of the project and write your data
 in quotes:

`TOKEN = ""`\
`BOT_NAME = ""`\
`HEROKU_DEPLOY_DOMAIN = ""`

From your dashboard on Heroku create a new app, once you create
 an app it will direct you to the deploy page, open the settings 
 tab in new window and copy the domain of the app which will be 
 something like https://appname.herokuapp.com/ and paste it in 
 the `HEROKU_DEPLOY_DOMAIN` variable inside our `credentials.py`
 
 now go back to the deploy tab and proceed with the steps:
* login to heroku

`$ heroku login`

note that sometimes this method get stuck in waiting for login,
 if this is the case with you, you can login using
 
`$ heroku login -i`

* Initialize a git repository in our directory

`$ git init`\
`$ heroku git:remote -a {heroku-project-name}`

* Deploy the app

`$ git add .`\
`$ git commit -m "first commit"`\
`$ git push heroku master`

at this point you will see the building progress in your terminal, 
if everything went okay you will see something like so

`remote: -----> Launching...`\
`remote:        Released v6`\
`remote:        https://project-name.herokuapp.com/ deployed to Heroku`\
`remote:`\
`remote: Verifying deploy... done.`

Now go to the app page (the link of the domain you copied before) 
and add to the end of the link `/setwebhook` so that the address will be 
something like `https://appname.herokuapp.com/setwebhook`, if you see `webhook 
setup ok` then you are ready to go!

# Deploying on Local Host (Ngrok)

Set `DEBUG = True` in settings.py

Download Ngrok from the link `https://ngrok.com/download`.
Carry out the following steps:

`$ ngrok http 8443`

Create a variable `NGROK_DEPLOY_DOMAIN = ""` in `credentials.py`  (created when deployed to Heroku)
and insert the specified address in quotes

![Image](app/static/NgrokCapture.PNG)

Now you can run `app.py` 
