#!/bin/bash

echo "=== Configurando Palabra Precisa en Codespaces ==="

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}1. Creando estructura de directorios...${NC}"
mkdir -p static/css static/js templates instance
mkdir -p uploads

echo -e "${BLUE}2. Creando entorno virtual...${NC}"
python3 -m venv venv

echo -e "${BLUE}3. Activando entorno virtual...${NC}"
source venv/bin/activate

echo -e "${BLUE}4. Actualizando pip...${NC}"
pip install --upgrade pip

echo -e "${BLUE}5. Instalando dependencias...${NC}"
pip install flask flask-sqlalchemy flask-login flask-wtf
pip install email-validator werkzeug python-dotenv

echo -e "${BLUE}6. Guardando dependencias...${NC}"
pip freeze > requirements.txt

echo -e "${BLUE}7. Creando archivo .env...${NC}"
cat > .env << ENVEOF
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=clave_secreta_$(date +%s | sha256sum | base64 | head -c 32)
DATABASE_URL=sqlite:///palabras.db
ENVEOF

echo -e "${BLUE}8. Inicializando base de datos...${NC}"
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✓ Base de datos creada')
"

echo -e "${GREEN}=== Instalación completada exitosamente ===${NC}"
echo -e "${GREEN}Para iniciar la aplicación:${NC}"
echo "  source venv/bin/activate"
echo "  flask run"
echo ""
echo -e "${GREEN}Luego abre el puerto 5000 en Codespaces${NC}"
