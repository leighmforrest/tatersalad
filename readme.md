#TaterSalad#

###Multi-User Journal Dimension###
by [Leigh Michael Forrest](http:leighmforrest.github.io/portfolio)

---
##Installing TaterSalad##

To install, clone the git repository with the folowing command:  `git clone https://github.com/leighmforrest/tatersalad.git`. In addition, the Google App Engine SDK must be installed. See [Google Cloud Platform](https://cloud.google.com/appengine/docs/python/download) for details.

At the top of the security.py file, there is a constant called `APP_SECRET`. You may change this constant to any string you like, but you must set it before **any** data is persisted. **It is highly recommended that the `APP_SECRET` is kept secret by using environment variables.** Check your system for details.

To deploy the app, run this command in the terminal: `gcloud app deploy  index.yaml app.yaml`. The index.yaml is needed for the database to run smoothly in production.

The installer may customize the templates to suit his or her tastes. Much of the templates rely on [The Bootstrap Framework](http://getbootstrap.com), so keep this in mind.
