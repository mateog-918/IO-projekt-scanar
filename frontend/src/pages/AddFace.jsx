import React, { useState, useEffect } from 'react';
import Swal from 'sweetalert2';

const AddFace = () => {
  const [employees, setEmployees] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [fileInputKey, setFileInputKey] = useState(Date.now());

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/manage_employees/');
      const data = await response.json();
      setEmployees(Array.isArray(data) ? data : data.employees || []);
    } catch (error) {
      console.error("Błąd pobierania:", error);
    } finally {
      setLoading(false);
    }
  };

  const resetFileState = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setFileInputKey(Date.now());
  };

  const handleEmployeeChange = (e) => {
    setSelectedId(e.target.value);
    resetFileState();
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleUpload = async () => {
    // --- NOWA LOGIKA WALIDACJI Z POPUPAMI ---
    if (!selectedId && !selectedFile) {
      Swal.fire({
        icon: 'warning',
        title: 'Brak danych',
        text: 'Musisz wybrać pracownika ORAZ dodać zdjęcie przed kliknięciem Upload.',
        confirmButtonColor: '#00cae9'
      });
      return;
    }

    if (!selectedId) {
      Swal.fire({
        icon: 'warning',
        title: 'Wybierz pracownika',
        text: 'Proszę wskazać pracownika z listy rozwijanej.',
        confirmButtonColor: '#00cae9'
      });
      return;
    }

    if (!selectedFile) {
      Swal.fire({
        icon: 'warning',
        title: 'Dodaj zdjęcie',
        text: 'Proszę wybrać plik graficzny z dysku.',
        confirmButtonColor: '#00cae9'
      });
      return;
    }

    // Jeśli walidacja przeszła pomyślnie, kontynuujemy wysyłkę
    const formData = new FormData();
    formData.append('image', selectedFile);

    setUploading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/manage_employees/${selectedId}/faces`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        await Swal.fire({
          icon: 'success',
          title: 'Sukces!',
          text: 'Zdjęcie zostało pomyślnie przypisane do pracownika.',
          timer: 2000,
          showConfirmButton: false
        });
        resetFileState();
      } else {
        const errorData = await response.json();
        Swal.fire('Błąd serwera', errorData.message || 'Wystąpił problem przy zapisie.', 'error');
      }
    } catch (error) {
      Swal.fire('Błąd połączenia', 'Brak komunikacji z backendem.', 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="form-container">
      <div className="input-group-row">
        <div className="input-field">
          <label>Select Employee</label>
          <select
            className="custom-select"
            value={selectedId}
            onChange={handleEmployeeChange}
            disabled={loading}
          >
            <option value="">Choose an employee...</option>
            {employees.map((emp) => (
              <option key={emp.id} value={emp.id}>{emp.name}</option>
            ))}
          </select>
        </div>

        <div className="input-field">
          <label>Upload Face Picture</label>
          <input
            key={fileInputKey}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
          />
        </div>

        {/* Przycisk jest teraz odblokowany, aby można było wywołać walidację kliknięciem */}
        <button
          className="btn-main"
          onClick={handleUpload}
          disabled={uploading || loading}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>

      <div className="qr-code-display">
        <label>Photo preview:</label>
        <div className="image-preview-wrapper">
          {previewUrl ? (
            <img src={previewUrl} alt="Preview" className="face-preview-img" />
          ) : (
            <div className="preview-placeholder">No photo selected</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AddFace;