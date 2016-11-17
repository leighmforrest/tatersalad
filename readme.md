#TaterSalad#

###Multi-User Journal Dimension###
by [Leigh Michael Forrest](http:leighmforrest.github.io/portfolio)
[https://tatersalad-149702.appspot.com/](https://tatersalad-149702.appspot.com/)

---
##Installing TaterSalad##

To install, clone the git repository with the folowing command:  `git clone https://github.com/leighmforrest/tatersalad.git`. In addition, the Google App Engine SDK must be installed. See [Google Cloud Platform](https://cloud.google.com/appengine/docs/python/download) for details.

At the top of the security.py file, there is a constant called `APP_SECRET`. You may change this constant to any string you like, but you must set it before **any** data is persisted. **It is highly recommended that the `APP_SECRET` is kept secret by using environment variables.** Check your system for details.

To run the app on the local machine, `cd` into the root directory (the directory
that contains `app.yaml') and run the following command in the terminal: `dev_appserver.py .` It will
be greatly suggested to uncomment the lines in `main.py` that contain `time.sleep(<seconds>)`
before running this command. You may be forwarded to a post that may not yet exist in the database.

To deploy the app, `cd` into the root directory and run this command in the terminal: `gcloud app deploy  index.yaml app.yaml`. The index.yaml is needed for the database to run smoothly in production.

The installer may customize the templates to suit his or her tastes. Much of the templates rely on [The Bootstrap Framework](http://getbootstrap.com), so keep this in mind.
