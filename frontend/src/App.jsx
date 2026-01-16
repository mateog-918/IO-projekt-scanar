import {BrowserRouter as Router, Routes, Route, useLocation, Navigate, useNavigate} from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import Login from './pages/Login.jsx';
import AddEmployee from './pages/AddEmployee.jsx';
import Verify from './pages/Verify.jsx';
import VerifyFace from "./pages/VerifyFace.jsx";
import GenerateQR from './pages/GenerateQR.jsx';
import AddFace from './pages/AddFace.jsx';
import RemoveEmployee from './pages/RemoveEmployee.jsx';
import Reports from './pages/Reports.jsx';
import EmployeeList from "./pages/EmployeeList.jsx";
import React, { useState, useEffect } from 'react';
import './App.css';
import logo from './assets/Logo.png';
import Swal from "sweetalert2";

// Tworzymy pomocniczy komponent, aby móc użyć useLocation()
function AppContent() {
    const location = useLocation();
    const [auth, setAuth] = useState({ loggedIn: false, username: null, loading: true });

    // Wyciągamy funkcję sprawdzającą do osobnej zmiennej, aby móc ją wywołać wielokrotnie
    const checkAuth = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/auth/status', {credentials: 'include'});
            const data = await response.json();
            setAuth({
                loggedIn: data.logged_in,
                username: data.username,
                loading: false
            });
        } catch (error) {
            setAuth({ loggedIn: false, username: null, loading: false });
        }
    };

    // Nowa funkcja do wylogowania
    const handleLogout = async () => {
        try {
            // Wysyłamy zapytanie POST do API
            const response = await fetch('http://localhost:5000/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Jeśli serwer wymaga przesyłania ciasteczek/sesji, dodaj: credentials: 'include'
                credentials: 'include',
            });

            if (response.ok) {
                // 2. Wyświetlamy komunikat o sukcesie
                Swal.fire({
                    icon: 'info',
                    title: 'Wylogowano',
                    text: 'Zostałeś pomyślnie wylogowany',
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                // Obsługa błędu serwera (np. 500)
                Swal.fire({
                    icon: 'error',
                    title: 'Błąd',
                    text: 'Wylogowanie nie powiodło się na serwerze.',
                });
            }
            const statusResponse = await fetch('http://localhost:5000/api/auth/status', {credentials: 'include'});
            const data = await statusResponse.json();
            setAuth({
                loggedIn: data.logged_in,
                username: data.username,
                loading: false
            });
        } catch (error) {
            // Obsługa błędu sieci (brak połączenia)
            console.error("Logout error:", error);
            Swal.fire({
                icon: 'error',
                title: 'Błąd połączenia',
                text: 'Nie udało się połączyć z serwerem, ale sesja lokalna zostanie zamknięta.',
            });
        }
    };

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        checkAuth();
    }, []); // Sprawdzamy tylko raz przy starcie aplikacji

    if (auth.loading) return <div>Ładowanie...</div>;

    const hideSidebar = location.pathname === "/" || location.pathname === "/verify-face";
    const publicPaths = ["/", "/login", "/verify-face"];
    const isAccessDenied = !auth.loggedIn && !publicPaths.includes(location.pathname);

    return (
        <div className="app-layout">
            <div className="app-header">
                <img src={logo} alt="SCANAR Logo" className="logo" />
            </div>

            <div className={`app-container ${hideSidebar ? 'no-sidebar' : ''}`}>
                {!hideSidebar && <Sidebar isLoggedIn={auth.loggedIn} />}

                <main className="main-content">
                    {isAccessDenied && <Navigate to="/login" replace />}

                    <Routes>
                        <Route path="/" element={<Verify />} />
                        {/* PRZEKAZUJEMY FUNKCJĘ checkAuth DO KOMPONENTU LOGIN */}
                        <Route path="/login" element={<Login auth={auth} onLoginSuccess={checkAuth} onLogout={handleLogout} />} />
                        <Route path="/generate-qr" element={<GenerateQR />} />
                        <Route path="/add-employee" element={<AddEmployee />} />
                        <Route path="/add-face" element={<AddFace />} />
                        <Route path="/remove-employee" element={<RemoveEmployee />} />
                        <Route path="/reports" element={<Reports />} />
                        <Route path="/verify-face" element={<VerifyFace />} />
                        <Route path="/employee-list" element={<EmployeeList />} />
                    </Routes>
                </main>
            </div>
        </div>
    );
}

// Główny komponent tylko renderuje Router
function App() {
    return (
        <Router>
            <AppContent />
        </Router>
    );
}

export default App;