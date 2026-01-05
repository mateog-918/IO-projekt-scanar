import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from "html5-qrcode";
import { useNavigate, useLocation } from 'react-router-dom';
import Swal from 'sweetalert2';

const VerifyFace = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const employeeId = location.state?.employeeId;

  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const scannerRef = useRef(null);
  const isInitializing = useRef(false); // BEZPIECZNIK

  useEffect(() => {
  const savedLockout = localStorage.getItem('lockoutUntil');
    if (savedLockout && parseInt(savedLockout) > Date.now()) {
      navigate('/'); // Przekieruj do licznika czasu
      return;
    }

    if (!employeeId) {
    Swal.fire('Błąd', 'Brak identyfikatora.', 'error').then(() => navigate('/'));
    return;
  }

  // Używamy zmiennej lokalnej do śledzenia czy komponent jest zamontowany
  let isMounted = true;

  const init = async () => {
    if (isMounted) {
      await startCamera();
    }
  };

  init();

  return () => {
    isMounted = false; // Zabezpieczenie przed wywołaniem startu po odmontowaniu
    stopCamera();
  };
}, [employeeId]);

  const startCamera = async () => {
    // Sprawdzamy czy już nie skanujemy lub nie inicjalizujemy
    if (isInitializing.current || scannerRef.current?.isScanning) return;

    isInitializing.current = true;

    // Czyścimy kontener przed startem (na wszelki wypadek)
    const container = document.getElementById("reader");
    if (container) container.innerHTML = "";

    const html5QrCode = new Html5Qrcode("reader");
    scannerRef.current = html5QrCode;

    try {
      await html5QrCode.start(
        { facingMode: "user" },
        { fps: 20, qrbox: { width: 300, height: 300 }},
        () => {} // Ignorujemy skanowanie kodów, bo chcemy tylko podgląd
      );
      setIsCameraActive(true);
    } catch (err) {
      console.error("Błąd kamery:", err);
    } finally {
      isInitializing.current = false;
    }
  };

  const stopCamera = async () => {
  if (scannerRef.current) {
    try {
      // Sprawdzamy stan skanera przed próbą zatrzymania
      // Stan 2 oznacza SCANNING (uruchomiony)
      if (scannerRef.current.getState() === 2) {
        await scannerRef.current.stop();
      }
    } catch (err) {
      // Ignorujemy błąd "Cannot stop", bo oznacza on, że kamera i tak nie działa
      if (!err.includes("not running")) {
        console.warn("Błąd podczas zatrzymywania kamery:", err);
      }
    } finally {
      // Zawsze czyścimy referencje i DOM
      const container = document.getElementById("reader");
      if (container) container.innerHTML = "";
      scannerRef.current = null;
      setIsCameraActive(false);
    }
  }
};

  const handleCaptureAndVerify = async () => {
    if (isProcessing || !isCameraActive) return;

    const video = document.querySelector('#reader video');
    if (!video) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    setIsProcessing(true);
    await stopCamera();

    canvas.toBlob(async (blob) => {
      if (!blob) {
        setIsProcessing(false);
        startCamera();
        return;
      }

      const formData = new FormData();
      formData.append('employee_id', employeeId);
      formData.append('image', blob, 'face_capture.jpg');

      try {
        const response = await fetch(`http://localhost:5000/api/verification/employees/${employeeId}/match`, {
          method: 'POST',
          body: formData,
        });

        // Sprawdzamy czy odpowiedź jest poprawnym formatem JSON
        const result = await response.json();

        if (response.ok && result.match === true) {
          localStorage.setItem('failedAttempts', '0');
          localStorage.removeItem('lockoutUntil');
          // SCENARIUSZ: Sukces - twarze pasują
          Swal.fire({
            icon: 'success',
            title: 'Zweryfikowano',
            text: 'Tożsamość potwierdzona poprawnie.',
            timer: 2000,
            showConfirmButton: false
          }).then(() => navigate('/'));

        } else if (result.match === false) {
          // SCENARIUSZ: Brak dopasowania (match: false)
          const errorMsg = result.match === false ? 'Twarz nie pasuje.' : (result.error || 'Błąd serwera');
          handleFailure(errorMsg);
        } else {
          // SCENARIUSZ: Błąd po stronie serwera (np. 400, 500) lub brak pola match
          handleFailure('Błąd połączenia z serwerem');
        }

      } catch (err) {
        // SCENARIUSZ: Błędy sieciowe lub rzucone wyjątki powyżej
        Swal.fire({
          icon: 'error',
          title: 'Odmowa dostępu',
          text: err.message || 'Nie udało się połączyć z serwerem.',
          confirmButtonText: 'Spróbuj ponownie'
        }).then(() => {
          stopCamera();
          navigate('/');// Restart kamery, aby użytkownik mógł spróbować jeszcze raz
        });
      } finally {
        setIsProcessing(false);
      }
    }, 'image/jpeg', 0.9);
  };

  const handleFailure = (msg) => {
    const currentAttempts = parseInt(localStorage.getItem('failedAttempts')) || 0;
    const newAttempts = currentAttempts + 1;
    localStorage.setItem('failedAttempts', newAttempts.toString());

    if (newAttempts >= 5) {
      const unlockTime = Date.now() + 120000;
      localStorage.setItem('lockoutUntil', unlockTime.toString());
      Swal.fire('Zablokowano', 'Zbyt wiele prób (QR + Twarz). Czekaj 2 minuty.', 'error')
        .then(() => navigate('/'));
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Odmowa',
        text: `${msg} Pozostało prób: ${5 - newAttempts}`,
        confirmButtonText: 'Spróbuj ponownie'
      }).then(() => navigate('/'));
    }
  };

  return (
    <div className="verify-container">
        <div
          id="reader"
          className={isCameraActive ? "scanner-active" : "scanner-hidden"}
          style={{ width: '100%', maxWidth: '500px' }} // Dodatkowe zabezpieczenie szerokości
        ></div>

        {isProcessing && (
          <div className="processing-overlay">
            <p>Weryfikacja...</p>
          </div>
        )}

      <div className="controls">
        <button
          className="btn-main btn-large"
          onClick={handleCaptureAndVerify}
          disabled={!isCameraActive || isProcessing}
        >
          {isProcessing ? "Czekaj..." : "Potwierdź Tożsamość"}
        </button>
      </div>
    </div>
  );
};

export default VerifyFace;