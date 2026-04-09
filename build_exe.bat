@echo off
setlocal

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

pyinstaller --noconfirm --clean --name FitShopAssistant --windowed --onefile run.py

echo Build complete. EXE is in dist\FitShopAssistant.exe
endlocal
