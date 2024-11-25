#config.py
class Config:
    SECRET_KEY = 'sua_chave_secreta'  # Coloque uma chave secreta forte
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/chat_app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 