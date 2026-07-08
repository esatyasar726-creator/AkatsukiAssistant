# Hafif ve güncel bir Python imajı kullanıyoruz
FROM python:3.11-slim

# Çalışma dizinini ayarlıyoruz
WORKDIR /app

# Gerekli bağımlılık listesini kopyalayıp yüklüyoruz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projedeki tüm kodları (main.py, banner_data.py vb.) içeri kopyalıyoruz
COPY . .

# Botu çalıştıracak komut
CMD ["python", "main.py"]

