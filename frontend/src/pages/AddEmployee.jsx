import React, { useState } from 'react';
import Swal from 'sweetalert2';

const AddEmployee = () => {
  const [formData, setFormData] = useState({ fullName: '', position: '', department: '' });
  const [loading, setLoading] = useState(false);

  const handleAddEmployee = async (e) => {
    // 1. Zawsze wywołuj preventDefault(), aby formularz nie odświeżył strony
    e.preventDefault();

    // 2. Walidacja manualna (JS)
    // .trim() usuwa spacje z początku i końca, zapobiegając wpisaniu samych spacji
    if (!formData.fullName.trim() || !formData.position.trim() || !formData.department.trim()) {
      Swal.fire({
        icon: 'warning',
        title: 'Puste pola',
        text: 'Wszystkie pola muszą zostać uzupełnione!',
      });
      return; // Przerywamy funkcję, fetch się nie wykona
    }

    const payload = {
      name: formData.fullName,
      position: formData.position,
      department: formData.department
    };

    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/manage_employees/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        Swal.fire('Sukces!', 'Pracownik dodany.', 'success');
        setFormData({ fullName: '', position: '', department: '' });
      } else {
        throw new Error('Błąd serwera');
      }
    } catch (error) {
      Swal.fire('Błąd!', 'Serwer nie odpowiada.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      {/* 3. Używamy tagu <form> i zdarzenia onSubmit zamiast onClick na przycisku */}
      <form className="form-container" onSubmit={handleAddEmployee}>
        <div className="input-group-row">
          <div className="input-field">
            <label>Full Name</label>
            <input
              type="text"
              value={formData.fullName}
              onChange={(e) => setFormData({...formData, fullName: e.target.value})}
              required // Walidacja HTML5 (pokazuje dymek w przeglądarce)
            />
          </div>
          <div className="input-field">
            <label>Position</label>
            <input
              type="text"
              value={formData.position}
              onChange={(e) => setFormData({...formData, position: e.target.value})}
              required
            />
          </div>
        </div>

        <div className="input-group-row">
          <div className="input-field">
            <label>Department</label>
            <input
              type="text"
              value={formData.department}
              onChange={(e) => setFormData({...formData, department: e.target.value})}
              required
            />
          </div>
          {/* Typ submit sprawia, że przycisk reaguje na Enter i aktywuje walidację 'required' */}
          <button type="submit" className="btn-main" disabled={loading}>
            {loading ? 'Adding...' : 'Add'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddEmployee;