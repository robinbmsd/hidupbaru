import random
import string
import time
import os
#   import = perintah untuk "memanggil" atau "meminjam" alat/fungsi dari tempat lain
#   os = (1) Operating System, ini library untuk berinteraksi dengan OS bawaan (Windows, Linux, MacOS) secara portable.
#   (2) Modul ini memungkinkan user mengelola folder, path, dan environments variable dan controlling the os untuk kebutuhan di API ini.
#   kenapa dibutuhkan? Kenapa dibutuhkan? Karena kita mau ambil username & password yang disimpan di environment variable (lebih aman daripada tulis langsung di code)
import random
#   random = digunakan untuk menghasilkan nilai acak (angka, pilihan karakter, urutan)
import string
#   string = menyediakan kumpulan karakter siap pakai (huruf, digit, simbol)
import time
#   time = berhubungan dengan waktu: delay, timestamp, dan pengukuran durasi eksekusi
import requests
#   requests = library untuk kirim HTTP request (GET, POST, dll) dan berkomukiasi dengan server lain
#   kenapa dibutuhkan? karena kita mau kirim data ke API Sumpahpalapa (yang ada di http://horven-api.sumpahpalapa.com)
from requests.auth import HTTPBasicAuth
#   from ... import ... = mengambil fungsi spesifik dari library
#   requests.auth = digunakan untuk menangani autentikasi saat mengirim permintaan HTTP.
#   HTTPBasicAuth = digunakan untuk basic authentication (username dan password standar)
#   kenapa dibutuhkan? API SumpahPalapa butuh login pakai username dan password
from datetime import datetime
#   datetime = library untuk kerja dengan tanggal dan waktu
#   kenapa dibutuhkan? kita mau catat kapan API mulai dan selesai (untuk logging/monitoring)
from fastapi import FastAPI, status
#   FastAPI = (1) framework untuk bikin API dengan Python (ini seperti "kerangka" atau "template" yang sudah jadi)
#   (2)jika dibandingkan dengan framework lain seperti Flask atau Django, FastAPI unggul dalam hal:
#   (2a) validasi data: otomatis memvalidasi input dari user. Jika user mengirim string padahal sistem meminta angka (int), FastAPI akan otomatis mengirim pesan error yang rapi.
#   (2b) keamanan: Mendukung OAuth2 dengan JWT tokens secara bawaan.
#   (2c) standar terbuka: dibuat berdasarkan standar OpenAPI dan JSON Schema.
#   status = kode status HTTP (200 = OK, 404 = Not Found, dll)
#   kenapa dibutuhkan? ini adalah backbone dari API yang sedang dibuat
from fastapi.responses import JSONResponse
#   responses = sub module FastApi yang berfungsi untuk menyediakan feedback dari API yang sudah dibuat ke Client (aplikasi atau end user)
#   JSONResponse = (1) class dari responses yang mengubah objek Python menjadi string JSON standar.
#   (2) objek Python = data = {"nama": "Budi", "umur": 20}
#   (3) string JSON standar = (3a) Tipe Data = Mengubah True (Python) menjadi true (JSON/kecil semua).
#   (3b) Tipe Data = Mengubah None (Python) menjadi null (JSON).
#   (3c) String = Memastikan semua petik menggunakan petik dua (" "), karena JSON tidak mau pakai petik satu (' ').
#   kenapa dibutuhkan? untuk melakukan serialisasi data Python ke format JSON yang sesuai standar protokol HTTP, sekaligus memberikan kontrol penuh terhadap status code dan header dalam siklus request-response.
from pydantic import BaseModel
#   pydantic = (1) library untuk validasi data dan settings management.
#   (2) Pydantic memastikan bahwa data yang masuk ke API memiliki format dan tipe yang benar. jika data tidak sesuai, Pydantic akan memberikan pesan error yang sangat jelas.
#   BaseModel = (1) class dasar dari Pydantic untuk mendefinisikan struktur data, skema, dan aturan validasi. 
#   (2) semacam blueprint yang memastikan setiap bahan bangunan (data) yang masuk memiliki ukuran dan tipe yang tepat.
#   kenapa dibutuhkan? biar bisa define struktur data yang diterima API dengan rapi (misal: harus ada customer_id, product_code, dll)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
#   cryptography = library untuk menyembunyikan data agar tidak bisa dibaca orang lain (Encrypt) dan membukanya kembali (Decrypt)
#   hazmat = (1) singkatan dari Hazardous Materials (bahan berbahaya). 
#   (2) sub module dari cryptography, mengatur mode enscrypt dan decrypt secara manual. 
#   (3) masuk ke low level, karena menyediakan akses ke sub module kriptografi yang mendukung sampai ke bagian dasar yaitu cipher.
#   primitives = sub module dari hazmat, berfungsi sebagai sub package untuk mendukung securoty sistem yang utuh dan mendukung untuk mengakses chiper.
#   ciphers = algoritma untuk melakukan enkripsi dan dekripsi. Ini adalah prosedur langkah-demi-langkah untuk mengubah teks biasa (plaintext) menjadi kode rahasia (ciphertext) dan sebaliknya.
#   jadi, cryptography.hazmat.primitives.ciphers = (1) jalur path lengkap dari library cryptography untuk melakukan encrypt dan decrypt.
#   (2) Artinya: "penggunaan fitur Cipher (enkripsi), yang merupakan sebuah Primitive (komponen dasar), yang berada di dalam sub module Hazmat (area teknis berbahaya) milik library Cryptography."
#   1. import 'Cipher, algorithms, modes'
#   2. Cipher = class untuk menyatukan algorithms dan modes.
#   algorithms = fungsi matematika yang menentukan bagaimana bit-bit data akan diacak berdasarkan kunci (key) yang kamu berikan.
#   modes = prosedur operasional yang mengatur bagaimana sebuah algorithm (yang punya keterbatasan ukuran data) bekerja pada data yang panjangnya fleksibel.
#   default_backed = function yang berfungsi secara otomatis os yang diakapai (windows, mac, linux, etc)
#   backend = sub module dari hazmat yang berfungsi sebagai engine untuk menjalankan function2 sepertin default_backend
#   kenapa dibutuhkan? sebagai keamanan data yang dikirim dari device pengguna yang dienkrip dulu, lalu di decrypt di API ini untuk memastikan agar request-nya legitimate.
api_url = "http://horven-api.sumpahpalapa.com/api/transaction/mobile.json"
#   api_url = variabel untuk menyimpan URL untuk top up pulsa
#   kenapa dibutuhkan? sebagai destination adress untuk kirim request
username = os.environ["alterra_username"]
password = os.environ["alterra_pwd_dev"]
#   username = variabel untuk menyimpan username
#   password = variabel untuk menyimpan passsword
#   ["alterra_username"] = mengambil nilai dari environment variable (dari os) bernama alterra_username
#   ["alterra_password"] = mengambil nilai dari environment variable (dari os) bernama alterra_password
def decrypt_Auth(ciphertext_hex, nonce_hex, tag_hex, execMode):
#   def = singkatan dari 'define', fungsinya untuk memberi perintah untuk membuat fungsi baru
#   decrypt_Auth = nama fungsinya (decrypt = buka kunci, Auth = authentication/autentikasi)
#   parameter - ciphertext_hex = teks yang sudah dienkrip (dalam format hexadecimal)
    #Analogi sederhana -> ciphertext_hex = barang yang dikunci dalam brankas
#   parameter - nonce_hex = angka random yang cuma dipakai sekali (Number used ONCE)
#   parameter - tag_hex = tag untuk verifikasi keaslian data
    #Analogi sederhana -> nonce_hex dan tag_hex = kombinasi kunci brankas
#   parameter - execMode = mode eksekusi ("DEV" untuk development, "PROD" untuk production)
#   #Analogi sederhana -> execMode = mode keamanan (DEV atau PROD)
    if execMode == "DEV":
#   if execMode == "DEV": = kalau mode-nya development
        hex_key = os.environ["HEX_KEY"]
#       hex_key = os.environ["HEX_KEY"] = ambil kunci dari environment variable namanya "HEX_KEY"
#       os.environ["..."] = ambil nilai dari sistem operasi (lebih aman dari hardcode)
    else:
#   else: = kalau bukan DEV (misalnya PROD)
        hex_key = ""
#   hex_key = "" = kunci kosong (di production seharusnya ada kunci lain)
    key = bytes.fromhex(hex_key)
#   bytes.fromhex() = fungsi untuk convert dari hexadecimal ke bytes
    ciphertext = bytes.fromhex(ciphertext_hex)
#   digunakan untuk convert data yang dienkrip dari hex ke bytes. ini data asli yang mau kita buka
    nonce = bytes.fromhex(nonce_hex)
#   nonce = (1) singkatan dari "number only used once". 
#   (2) berfungsi untuk acak angka yang cuma dipakai sekali, agar enkripsi lebih aman
    tag = bytes.fromhex(tag_hex)
#   tag = segel digital untuk verifikasi data belum diubah user lain
#   berfungsi untuk convert authentication tag dari hex ke bytes
    
    #Inti dari Hazmat
    decryptor = Cipher(
#   decryptor = Cipher(...).decryptor()
#   decryptor = variabel yang menyimpan object decrypt yang dibuat oleh Cipher(...).decryptor().
#   jadi,
#   decryptor = Cipher(...).decryptor() adalah
#   decryptor = variabel
#   Cipher(...).decryptor() = proses pembuatan object
#   Cipher = class dari library cryptography untuk melakukan enkripsi/dekripsi
        algorithms.AES(key),
#   algorithms.AES = mengakses Attribute AES dari module algorithms
#   
        modes.GCM(nonce, tag),
#   modes.GCM = mengakses Attribute GCM dari module modes
        backend=default_backend()
#   default_backend() = lihat line 53
#   backend = lihat line 54
    ).decryptor()
#   jadi,
#   decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend()).decryptor()
#   itu sama dengan decryptor = Cipher(...).decryptor()
#   dimana,
#   decryptor = variabel
#   Cipher(...).decryptor() = proses pembuatan object?
#   Cipher = class?
#   (...) = (algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend()) = arguments?
#   Cipher(...) = Constructor?
#   algorithms = module
#   modes = module
#   AES = class?
#   algorithms.AES = Attribute
#   modes.GCM = Attribute
#   GCM = class
#   key (secret key), nonce (unique number) dan tag (digital safter seal) ->(2)
#   ->(2) Data dari key = bytes.fromhex(hex_key), nonce = bytes.fromhex(nonce_hex), tag = bytes.fromhex(tag_hex)
#   .decryptor() = method? kenapa harus pakai '.'? kenapa ga decryptor() saja?
#   Titik (.) dalam coding, titik itu ibarat Alamat atau Kepemilikan.
#   Bayangkan kamu punya dua benda: TV dan AC. Keduanya punya tombol Power.
#   Jika kamu menulis TV.Power(), maka hanya TV yang menyala.
#   Jika kamu menulis AC.Power(), maka hanya AC yang menyala.
    try:
#   try = mencoba menjalankan kode di dalamnya
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
#   decryptor = cek line 98
#   decryptor.update(ciphertext) = object.method(parameter)
#   ciphertext = cek line 86
    except Exception as e:
#   except Exception as e: = kalau ada error apapun (Exception), catch errornya dan simpan detail errornya ke variabel e
        print(e)
#   pesan error-nya di console/terminal supaya programmer tahu error apa yang terjadi (untuk debugging)
        return False
    
    return plaintext.decode("utf-8")