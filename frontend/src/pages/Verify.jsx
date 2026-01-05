import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from "html5-qrcode";
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';

const Verify = () => {
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    return () => {
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

      if (response.status === 200 && data.success) {
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

      } else if (response.status === 400 || response.status === 404) {
        // BŁĄD: 400 (Brak danych) lub 404 (Nie znaleziono)
        Swal.fire({
          icon: 'error',
          title: 'Weryfikacja nieudana',
          text: data.message,
        });

      } else {
        // Inne błędy (np. 500)
        throw new Error('Błąd serwera');
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

  return (
    <div className="verify-container">
      <div
        id="reader"
        className={isScanning ? "scanner-active" : "scanner-hidden"}
      ></div>

      {!isScanning && (
        <div className="camera-viewport-placeholder">
          <div className="scan-corners"></div>
          <p>Camera is off</p>
        </div>
      )}

      <div className="controls">
        <button
          className="btn-main btn-large"
          onClick={startScanning}
          disabled={isScanning}
        >
          {isScanning ? "Scanning..." : "Verify QR"}
        </button>
      </div>
    </div>
  );
};

export default Verify;