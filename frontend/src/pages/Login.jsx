import React, { useState } from 'react';

const Login = () => {


  return (
    <div className="form-container">
        <div className="input-group-row">
            <div className="input-field">
                <label>Username</label>
                <input type="text"/>
            </div>
            <div className="input-field">
                <label>Password</label>
                <input type="text"/>
            </div>
            <button className="btn-main">Login</button>
        </div>
    </div>
  );
};

export default Login;