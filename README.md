# 🔐 SCANAR - System Kontroli Dostępu

**System weryfikacji dostępu pracowników z wykorzystaniem kodów QR i rozpoznawania twarzy**

Projekt stworzony na przedmiot Inżynieria Oprogramowania 


## 📋 Opis projektu

SCANAR to  rozwiązanie dla firm przemysłowych zarządzających zakładami pracy. System eliminuje nadużycia związane z przekazywaniem kart dostępowych między pracownikami poprzez dwuetapową weryfikację:

1. **Skanowanie kodu QR** - unikalny dla każdego pracownika
2. **Rozpoznawanie twarzy** - biometryczna weryfikacja tożsamości


### ✨ Rozwiązanie

System SCANAR łączy dwa mechanizmy weryfikacji:
- **QR Code** - potwierdzenie ważnej przepustki
- **Face Recognition** - identyfikacja osoby (tolerance: 0.6)
- **Logging** - rejestracja wszystkich prób wejścia
- **Reporting** - raporty dotyczące wykrytych nadużyć

---

## 🚀 Funkcjonalności

### 👨‍💼 Panel Administracyjny
- ✅ Zarządzanie pracownikami (CRUD)
- ✅ Generowanie unikalnych kodów QR
- ✅ Dodawanie zdjęć twarzy (maks. 5 na pracownika)
- ✅ Aktywacja/Dezaktywacja pracowników
- ✅ Usuwanie pracowników (hard delete z potwierdzeniem)
- ✅ Edycja danych (imię, stanowisko, dział)
- ✅ Usuwanie pojedynczych zdjęć twarzy

### 🔍 System Weryfikacji
- ✅ Weryfikacja kodu QR
- ✅ Porównanie twarzy z bazy danych
- ✅ Dwuetapowa weryfikacja (QR + Face)
- ✅ Obsługa kamer na żywo
- ✅ Automatyczne logowanie zdarzeń

### 📊 Logi i Raporty
- ✅ Kompletny dziennik zdarzeń
- ✅ Filtrowanie po typie zdarzenia
- ✅ Filtrowanie po pracowniku
- ✅ Filtrowanie po zakresie dat
- ✅ Statystyki zdarzeń
- ✅ Przechowywanie zdjęć z weryfikacji

### 🔐 Uwierzytelnianie
- ✅ Logowanie admina (session-based)
- ✅ Ochrona endpointów zarządzających
- ✅ Domyślne credentials: `admin` / `admin123`

---

## 🛠️ Stack Technologiczny

### Backend
- **Flask 3.0.0** - Framework webowy
- **SQLAlchemy 3.1.1** - ORM dla bazy danych
- **SQLite** - Baza danych (w folderze `/instance`)
- **Flasgger 0.9.7.1** - Dokumentacja API (Swagger UI)
- **face_recognition** - Biblioteka do rozpoznawania twarzy
- **opencv-python** - Przetwarzanie obrazów
- **qrcode** - Generowanie kodów QR
- **Pillow** - Manipulacja obrazami
- **Flask-CORS** - Obsługa CORS

### Frontend
- **React 19.2.0** - Biblioteka UI
- **Vite 6.0.5** - Build tool
- **React Router 7.1.3** - Routing
- **jspdf + jspdf-autotable** - Generowanie PDF





## 🤝 Autorzy
- Mateusz Gacek
- Jan Ogiegło
- Paweł Kowalcze

