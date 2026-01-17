import React, { useState } from 'react';
import Swal from 'sweetalert2';

const Login = ({ auth, onLoginSuccess, onLogout }) => {
    // Stany dla formularza
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('http://localhost:5000/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
                credentials: 'include',
            });

            const data = await response.json();

            if (response.ok) {
                // Status 200 - Logowanie udane
                if (onLoginSuccess) await onLoginSuccess();
                Swal.fire({
                    icon: 'success',
                    title: 'Zalogowano!',
                    text: data.message,
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                // Status 400, 401 lub inne błędy
                Swal.fire({
                    icon: 'error',
                    title: 'Błąd logowania',
                    text: data.message || 'Coś poszło nie tak',
                });
            }
        } catch (error) {
            // Błąd połączenia z serwerem
            Swal.fire({
                icon: 'error',
                title: 'Błąd serwera',
                text: 'Nie udało się połączyć z API',
            });
        }
    };


    // WIDOK PO ZALOGOWANIU (Zgodny z Twoim zdjęciem)
    if (auth.loggedIn) {
        return (
            <div className="form-container">
            <div style={{
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '40px',
                width: '100%',
                maxWidth: '800px'
            }}>
                <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#2c3e50', margin: 0 }}>
                    Witaj, {auth.username}!
                </h2>
                <button
                    className="btn-main"
                    onClick={onLogout}
                >
                    Wyloguj się
                </button>
            </div>
            </div>
        );
    }

    // Widok formularza logowania
    return (
        <div className="form-container">
            <form onSubmit={handleLogin} className="input-group-row">
                <div className="input-field">
                    <label>Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="input-field">
                    <label>Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className="btn-main">Login</button>
            </form>
        </div>
    );
};

export default Login;