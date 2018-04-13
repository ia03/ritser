install apache wsgi and make it run on startup

install postgresql and citext extension https://stackoverflow.com/questions/15981197/postgresql-error-type-citext-does-not-exist

set up postgresql database and make it run on startup
set environment variables in readme.md

install whatever is in requirements.txt

set debug to false

run collectstatic

minify css and js files

run python3 manage.py createinitialrevisions

change SITE_ID in settings.py

register api on reddit https://www.reddit.com/wiki/api

change reddit oauth settings(redirect uri) or create another oauth app for production and change client/app id in useragent

add reddit social application

run manage.py rebuild_index

make daily clearsessions and cleansuspended cron jobs

install mod_security and configure for apache