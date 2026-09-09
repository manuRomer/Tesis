Write-Host "Creando el entorno virtual..."
python -m venv venv

Write-Host "Activando el entorno..."
.\venv\Scripts\activate

Write-Host "Actualizando pip e instalando dependencias..."
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "¡Entorno listo y activado!"