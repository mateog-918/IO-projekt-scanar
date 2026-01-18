# Uruchamianie aplikacji Scanar - Windows

## Uruchamianie Backendu

1. Sklonuj repozytorium
2. Wejdź w IO-projekt-scanar directory
3. Zainstaluj python 3.11
4. Uruchom virtual environment (venv) ``` python -m venv vevn ```
5. Aktywuj venv ``` .\venv\Scripts\activate ```

6. ``` cd backend ```
7. ``` pip install -r requirements.txt ```
8. ``` python app.py ```
9. Backend powinien działać pod http://127.0.0.1:5000


## Uruchamianie Frontendu
1. Otwórz nowy terminal
2. Upewnij się, że masz zainstalowane środowisko Node.js. Możesz to sprawdzić, wpisując w terminalu: ```node -v```
3. Jeśli nie masz Node.js, pobierz go ze strony nodejs.org.
4. Ustaw directory na IO-projekt-scanar
5. Aktywuj venv ``` .\venv\Scripts\activate ```
6.  ```npm create vite@latest```
7. **Directory not empty. Continue?"** – Vite zapyta, czy kontynuować, ponieważ widzi Twoje pliki. Wybierz **Yes.**

8. **"Select a framework"** – Wybierz React.
9. **"Select a variant"** – Wybierz JavaScript
10. ```cd frontend```
11. ```npm install``` instaluje pakiety z package.json
15. ```npm run dev```

16. http://localhost:5173 - strona główna dla pracowników
17. http://localhost:5173/login -  strona dla admina