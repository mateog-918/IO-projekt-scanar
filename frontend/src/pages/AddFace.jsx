import React, { useState } from 'react';

const AddFace = () => {

    const [formData, setFormData] = useState({ fullName: ''});
    const employees = ["Jan Kowalski", "Anna Nowak", "Piotr Zieliński", "Maria Mazur"];

  return (
    <div className="form-container">
        <div className="input-group-row">
            <div className="input-field">
                <label>Select Employee</label>
                <select
                    className="custom-select"
                    onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                >
                    <option value="">Choose an employee...</option>
                    {employees.map((name, index) => (
                        <option key={index} value={name}>
                            {name}
                        </option>
                    ))}
                </select>
            </div>
            <div className="input-field">
                <label>Upload Face Picture (max 1)</label>
                <input type="file" accept="image/*" />
            </div>
            <button className="btn-main">Upload</button>
        </div>
        <div className="qr-code-display">
            <label>Photo preview</label>

        </div>
    </div>
  );
};

export default AddFace;