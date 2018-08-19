# users package

This is a package designed for use in a shotglass based flask web application. It provides Users and Roles functionallity 
as well as a Pref table to hold random preferences.

## Installation:

Clone next to a python 3.x virtualenv along with the packages listed below. Normally I expect this package to be cloned
into a [shotglass]("https://github.com/wleddy/shotglass") project as a starting point for a web app.

Users will provide all the database functionality for the starter site including

* database.Database: A class that provides a basic Sqlite3 connection.
* database.SqliteTable: A class that provides DDL and DML functions to tables sub-classed from it.
* models.User,Role,UserRole and Pref: Classes that define the tables used in this package. Copy one of these
classes into your new app to define more table as you need them.


### Required packages:

* python 3.x
* Flask and it's default dependencies, of course
* Flask-mail
* pytest
