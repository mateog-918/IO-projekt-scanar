# Full documentation of this project lives in /docs/html

## To generate new documentation:
### *IMPORTANT:* documentation already exist in /docs/html
### This commands will generate new documentation, delete the previous one. 
### Make sure to only do this if you contributed to the project and changed the comments under some functions
---
1. make sure you are in doc directory

<pre>
sphinx-apidoc -o ../docs/source ../backend/app
make clean
make html
</pre>