# SistemSPP_Sekolah_Flask

<p>
<justify> 
Sistem ini merupakan aplikasi berbasis web yang dibangun menggunakan Flask untuk membantu pengelolaan pembayaran SPP siswa di lingkungan sekolah.
</justify>
</p>

<h2>Pemasangan & Persiapan</h2>
<h4>1. Clone repositori</h4>
<p> git clone https://github.com/krisnasuma/SistemSPP_Sekolah_Flask.git</p>
<p> cd SistemSPP_Sekolah_Flask</p>

<h4>2. Aktifkan virtual environment (opsional)</h4>
<p>python -m venv venv </p>
<p> source venv/bin/activate  # Linux/macOS </p>
<p> venv\\Scripts\\activate   # Windows </p>

<h4>3. Install dependensi </h4>
<p> pip install -r requirements.txt </p>

<h4>4. Jalankan aplikasi </h4>
<p> pip install -r requirements.txt </p>

<h4>5. Jalankan aplikasi </h4>
<p> pip install -r requirements.txt </p>

<h4>6. Akses melalui browser </h4>
<p> http://localhost:5000 </p>

<h4>7. Masuk hanya melalui mode admin </h4>
<p> Usernane: admin </p>
<p> Password: admin123 </p>

<h2> Hasil Konsep Tampilan </h2>

<h4>🖼️ Tampilan Login</h4> 

![Login](LoginByAdminOnly.PNG)

<h4>🖼️ Tampilan Kelas</h4> 

![Kelas](TampilanKelas.PNG) <br>
![TambahKelas](TampilanTambahKelas.PNG) <br>
![EditKelas](TampilanEditKelas.PNG)

<h4>🖼️ Tampilan Siswa</h4> 

![Siswa](TampilanSiswa.PNG) <br>
![TambahSiswa](TampilanTambahSiswa.PNG) <br>
![EditSiswa](TampilanEditSiswa.PNG)

<h4>🖼️ Tampilan SPP</h4> 

![SPP](TampilanDataSPP.PNG) <br>
![TambahSPP](TampilanTambahDataSPP.PNG) <br>
![EditSPP](TampilanEditDataSPP.PNG)

<h4>🖼️ Tampilan Pembayaran</h4> 

![Pembayaran](TampilanDataPembayaran.PNG) <br>
![TambahPembayaran](TampilanDataTambahPembayaran.PNG) <br>
![EditPembayaran](TampilanEditDataPembayaran.PNG) <br>
![KwitansiPembayaran](TampilanKwitansiPembayaran.PNG)

<h4>🖼️ Dashboard </h4> 

![Dashboard](dashboard.PNG) <br>

<h2> Struktur Folder </h2>
├── __pycache__/ <br>
├── instance/ <br>
├── static/ <br>
├── templates/ <br>
├── app.py <br>
├── database.db <br>
├── requirements.txt <br>
├── README.md <br>

<h2> Alur Penggunaan </h2>
1. Isi dahulu halaman "Kelas". <br>
2. Isi halaman "SPP". <br>
2. Isi halaman "Siswa". <br>
3. Isi halaman "Pembayaran".

<h2> Fitur </h2>
1. Manajemen data siswa dan kelas. <br>
2. Input dan edit nominal SPP. <br>
3. Pencatatan transaksi pembayaran. <br>
4. Tampilan kwitansi pembayaran. <br>
5. Login khusus admin. <br>
6. Antarmuka berbasis HTML dan template Flask.

<h2> Tujuan Penggunaan </h2>
<p>
  Proyek ini bersifat open-source dan dapat digunakan untuk keperluan edukasi, pengembangan, atau modifikasi sesuai kebutuhan.
</p>










