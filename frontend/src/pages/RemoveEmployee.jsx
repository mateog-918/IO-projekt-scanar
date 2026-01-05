import React, { useState } from 'react';

const RemoveEmployee = () => {

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
            <button className="btn-main" style={{ backgroundColor: '#EF0000' }}>Remove from database</button>
        </div>
        <div className="information_display">
            <label>Information about: </label>

        </div>
    </div>
  );
};

export default RemoveEmployee;