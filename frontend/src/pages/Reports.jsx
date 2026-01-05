import React, { useState } from 'react';

const Reports = () => {

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
            <button className="btn-main">Check report</button>
        </div>
        <div className="qr-code-display">
            <label>Report of events:</label>

        </div>
    </div>
  );
};

export default Reports;