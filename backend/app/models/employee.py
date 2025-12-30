from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    qr_code_hash = db.Column(db.String(255), unique=True, nullable=False)
    face_encoding = db.Column(db.LargeBinary)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'qr_code_hash': self.qr_code_hash,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }