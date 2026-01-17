import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from "html5-qrcode";
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';

const Verify = () => {
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef(null);
  const navigate = useNavigate();
  const [failedAttempts, setFailedAttempts] = useState(() => {
    return parseInt(localStorage.getItem('failedAttempts')) || 0;
  });
  const [lockoutUntil, setLockoutUntil] = useState(() => {
    const saved = localStorage.getItem('lockoutUntil');
    return saved ? parseInt(saved) : null;
  });
  const [timeLeft, setTimeLeft] = useState(0);

  useEffect(() => {
    const checkLockout = () => {
      const now = Date.now();
      const savedLockout = localStorage.getItem('lockoutUntil');

      if (savedLockout) {
        const lockoutTime = parseInt(savedLockout);
        if (lockoutTime > now) {
          setLockoutUntil(lockoutTime);
          setTimeLeft(Math.ceil((lockoutTime - now) / 1000));
        } else {
          // Blokada minęła
          setLockoutUntil(null);
          setFailedAttempts(0);
          localStorage.removeItem('lockoutUntil');
          localStorage.setItem('failedAttempts', '0');
        }
      }
    };

    checkLockout();
    const timer = setInterval(checkLockout, 1000);
    return () => {
      clearInterval(timer);
      stopScanner();
    };
  }, []);

  const stopScanner = async () => {
    if (scannerRef.current && scannerRef.current.isScanning) {
      try {
        await scannerRef.current.stop();
        scannerRef.current = null;
      } catch (err) {
        console.warn("Error stopping scanner:", err);
      }
    }
  };

  const startScanning = async () => {
    if (lockoutUntil && Date.now() < lockoutUntil) {
      Swal.fire('Blokada', `Zbyt wiele prób. Spróbuj za ${timeLeft}s.`, 'warning');
      return;
    }
    if (isScanning) return;

    const html5QrCode = new Html5Qrcode("reader");
    scannerRef.current = html5QrCode;
    setIsScanning(true);

    const config = { fps: 10, qrbox: { width: 300, height: 300 } };

    try {
      await html5QrCode.start(
        { facingMode: "environment" },
        config,
        (decodedText) => {
          handleSuccess(decodedText);
        }
      );
    } catch (err) {
      console.error("Camera error:", err);
      setIsScanning(false);
      Swal.fire('Błąd', 'Brak dostępu do kamery', 'error');
    }
  };

  // --- NOWA LOGIKA WERYFIKACJI PRZEZ API ---
  const handleSuccess = async (result) => {
    await stopScanner();
    setIsScanning(false);

    try {
      const response = await fetch('http://localhost:5000/api/verification/qr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ qr_data: result }),
      });

      const data = await response.json();

      if (response.status === 200 && data.success && data.employee.is_active) {
        // SUKCES: 200 OK
        Swal.fire({
          icon: 'success',
          title: 'QR zweryfikowany!',
          text: data.message, // "Witaj, Jan Kowalski"
          timer: 2000,
          showConfirmButton: false
        }).then(() => {
          // Przekazujemy ID pracownika do widoku skanowania twarzy
          navigate('/verify-face', { state: { employeeId: data.employee.id } });
        });

      } else {
        let errorMessage = data.message || 'Weryfikacja nieudana';

        // Specyficzny komunikat dla nieaktywnego konta, które przyszło ze statusem 200
        if (response.status === 200 && data.employee && !data.employee.is_active) {
          errorMessage = 'Twoje konto jest nieaktywne. Skontaktuj się z administratorem.';
        }

        Swal.fire({
          icon: 'error',
          title: 'Weryfikacja nieudana',
          text: errorMessage,
        });

        // Tutaj wywołujemy Twoją logikę rejestrowania błędów (licznik prób)
        handleFailure(errorMessage);
      }

    } catch (error) {
      console.error("Verification error:", error);
      Swal.fire({
        icon: 'error',
        title: 'Błąd połączenia',
        text: 'Nie można skontaktować się z systemem weryfikacji.',
      });
    }
  };

  const handleFailure = (msg) => {
    const newAttempts = (parseInt(localStorage.getItem('failedAttempts')) || 0) + 1;
    setFailedAttempts(newAttempts);
    localStorage.setItem('failedAttempts', newAttempts.toString());

    if (newAttempts >= 5) {
      const unlockTime = Date.now() + 120000;
      setLockoutUntil(unlockTime);
      localStorage.setItem('lockoutUntil', unlockTime.toString());
      Swal.fire('Zablokowano', 'Przekroczono limit prób. Czekaj 2 minuty.', 'error');
    } else {
      Swal.fire('Błąd', `${msg}. Pozostało prób: ${5 - newAttempts}`, 'warning');
    }
  };

  return (
    <div className="verify-container">
      <div
        id="reader"
        className={isScanning ? "scanner-active" : "scanner-hidden"}
      ></div>

      {!isScanning && (
        <div className="camera-viewport-placeholder">
          <div className="scan-corners"></div>
          {lockoutUntil ? <p style={{color: 'red'}}>Blokada: {timeLeft}s</p> : <p>Gotowy do skanowania</p>}
        </div>
      )}

      <div className="controls">
        <button
          className="btn-main btn-large"
          onClick={startScanning}
          disabled={isScanning || lockoutUntil !== null}
        >
         {lockoutUntil ? `Zablokowane (${timeLeft}s)` : (isScanning ? "Skanowanie..." : "Skanuj QR")}
        </button>
      </div>
    </div>
  );
};

export default Verify;