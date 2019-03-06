# ACE JSON Editor READme

## Using Jdorn's JSON editor

A configuration editor for the SIMOC simulation. This program allows users to configure the seed data files for the agent model.


I set up a test http server using node.js and http-server module

In command line inside editor folder: 
http-server -c-1

(Could also use your local server method of choice i.e. Apache/httpd)
 
In browser:
http://localhost:8080


Main Page: Allows a user to tab through the various sections of the json library. A user can also import a custom json file as the library (but it must conform to the schema)

Reset to default sets all values based on the original library file. Revert changes undoes any chamge on the current tab.

Most of the properties of the JSON objects are defaulted to a collapsed state and need to be expanded for editing.

The user can modify the JSON directly with the "Edit Json" button. The "Object Properties" button should allow the user to add values into the json as well, but needs some additional testing.

Finally, the file can be downloaded via the "download config" button at the bottom of the page. Should probably be made more prominent.

 



