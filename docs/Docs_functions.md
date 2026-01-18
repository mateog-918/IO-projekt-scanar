# Dokumentacja funkcji

1. Wejdź w folder [docs/html](html)
2. Uruchom w przeglądarce plik [app.html](html/app.html)

## Generowanie nowej dokumentacji

Uwaga to usunie poprzenią dokumentację!

1. Upewnij się że jest w docs/ directory

<pre>
sphinx-apidoc -o ../docs/source ../backend/app
make clean
make html
</pre>