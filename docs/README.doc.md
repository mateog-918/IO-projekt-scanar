# Full documentation of this project lives in /docs/html

## To generate new documentation:
1. make sure you are in doc directory

<pre>
sphinx-apidoc -o ../docs/source ../backend/app
make clean
make html
</pre>