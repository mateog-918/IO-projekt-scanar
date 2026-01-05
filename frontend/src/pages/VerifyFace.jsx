import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from "html5-qrcode";
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';

const VerifyFace = () => {
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef(null);
  const navigate = useNavigate();

  // 1. Sprzątanie przy wychodzeniu z podstrony
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
        console.warn("Error stopping:", err);
      }
    }
  };

  const startScanning = async () => {
    // Zapobiegamy wielokrotnemu uruchomieniu
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
      Swal.fire('Error', 'No camera access', 'error');
    }
  };

  const handleSuccess = async (result) => {
    await stopScanner();
    setIsScanning(false);

    // Przykładowy warunek poprawności kodu
    if (result === "ADMIN-SCANAR-2026") {
      Swal.fire({
        icon: 'success',
        title: 'Verified!',
        text: 'Your face match was successful.',
        timer: 1500,
        showConfirmButton: false
      }).then(() => {
        navigate('/');
      });
    } else {
      Swal.fire({
        icon: 'error',
        title: 'Your face could not be verified',
        text: 'Try again!',
      }).then(() => {
        navigate('/');
      });
    }
  };

  return (
    <div className="verify-container">
      {/* KLUCZ: Kontener 'reader' musi być stale obecny w DOM.
        Zmieniamy tylko widoczność za pomocą opacity lub klasy.
      */}
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
          {isScanning ? "Scanning..." : "Verify your Face"}
        </button>
      </div>
    </div>
  );
};

export default VerifyFace;