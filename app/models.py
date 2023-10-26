from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import Bcrypt
from sqlalchemy.ext.hybrid import hybrid_property


db = SQLAlchemy()
bcrypt=Bcrypt()

class User(db.Model,SerializerMixin):
    __tablename__='users'
    serialize_rules = ('-houses.user',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False, unique=True)
    _password_hash=db.Column(db.String)



    houses = db.relationship('House',backref='user')

    def __repr__(self):
        return f'<The current user id {self.name}>'
    
    @hybrid_property
    def password_hash(self):
        raise AttributeError('password hash cannot be viewed')
    
   
    @password_hash.setter
    def password_hash(self,password): #method-hash pass before storing in db
        password_hash=bcrypt.generate_password_hash(
            password.encode('utf-8') #dfghoiuysxcv = @123
        )
        self._password_hash = password_hash.decode('utf-8')


    
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    

class House(db.Model,SerializerMixin):
    __tablename__='houses'
    serialize_rules = ('-user.houses',)

    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.Integer, unique=True)
    location = db.Column(db.String)

    user_id= db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<The house number is {self.no}>'

