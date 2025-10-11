##############IMPORT##########################

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os
from datetime import datetime

##############ENDLINE_IMPORT##################

# Membuat instance utama aplikasi Flask
# Argumen '__name__' digunakan agar Flask mengetahui lokasi file dan folder terkait (templates, static, dll.)

app = Flask(__name__)
#app = Flask(__name__, template_folder='/templates')

# Konfigurasi kunci rahasia (SECRET_KEY) digunakan untuk menjaga keamanan session dan perlindungan terhadap serangan CSRF.
# Di lingkungan produksi, sebaiknya diambil dari environment variable agar tidak mudah terbaca.
app.config['SECRET_KEY'] = 'rahasia-sekali' #Ganti dengan kunci rahasia yang kuat

# Menetapkan URI database untuk SQLAlchemy.
# Dalam hal ini, menggunakan SQLite dan membuat file database lokal bernama 'database.db'.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Menonaktifkan fitur track_modifications untuk menghemat resource dan menghindari warning dari SQLAlchemy.
# Karena fitur ini jarang dibutuhkan, disarankan untuk dimatikan.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) # Membuat instance utama SQLAlchemy
bcrypt = Bcrypt(app) # Membuat instance utama Bcrypt
login_manager = LoginManager(app) # Membuat instance utama LoginManager
login_manager.login_view = 'login' # Mengatur rute login jika pengguna belum login


#########Model Database#########

# Membuat model User untuk menyimpan informasi pengguna
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), nullable=False, default='admin')

# Membuat model Siswa
class Siswa(db.Model):
    nis = db.Column(db.String(20), primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    jenis_kelamin = db.Column(db.String(1))
    tanggal_lahir = db.Column(db.String(10))
    alamat = db.Column(db.Text)
    status = db.Column(db.String(20), default='aktif')
    
    kelas_id = db.Column(db.Integer, db.ForeignKey('kelas.id')) #new add
    kelas = db.relationship('Kelas', backref='siswa_list', lazy=True)

    @classmethod
    def search(cls, keyword): # classmethod mendefinisikan keyword untuk fitur pencarian (search) pada halaman Siswa
        return cls.query.filter(
            (cls.nama.ilike(f'%{keyword}%')) | 
            (cls.nis.ilike(f'%{keyword}%')) |
            (cls.alamat.ilike(f'%{keyword}%'))
        ).all()

# Membuat model Kelas
class Kelas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_kelas = db.Column(db.String(50), nullable=False)
    tingkat = db.Column(db.String(10)) # Contoh: 'Daycare', 'Preschool', 'TK A', 'TK B'
    wali_kelas = db.Column(db.String(100))
    
    keterangan = db.Column(db.Text) ##

    @classmethod
    def search(cls, keyword): # classmethod mendefinisikan keyword untuk fitur pencarian (search) pada halaman Kelas
        return cls.query.filter(
            (cls.nama_kelas.ilike(f'%{keyword}%')) |
            (cls.tingkat.ilike(f'%{keyword}%')) |
            (cls.wali_kelas.ilike(f'%{keyword}%'))
        ).all()


# Membuat model SPP
class SPP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tahun_ajaran = db.Column(db.String(20), nullable=False)
    nominal = db.Column(db.Float, nullable=False)
    keterangan = db.Column(db.Text)

    @classmethod
    def search(cls, keyword): # classmethod mendefinisikan keyword untuk fitur pencarian (search) pada halaman SPP
        return cls.query.filter(
            (cls.tahun_ajaran.ilike(f'%{keyword}%')) |
            (cls.keterangan.ilike(f'%{keyword}%'))
        ).all()

# Membuat model Pembayaran 
class Pembayaran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nis = db.Column(db.String(20), db.ForeignKey('siswa.nis'))
    id_spp = db.Column(db.Integer, db.ForeignKey('spp.id'))
    bulan = db.Column(db.String(20), nullable=False)
    tahun = db.Column(db.String(4), nullable=False)
    tanggal_bayar = db.Column(db.Date, nullable=False)
    #tanggal_bayar = db.Column(db.String(10), nullable=False)
    jumlah = db.Column(db.Float, nullable=False)
    metode_pembayaran = db.Column(db.String(20))
    status = db.Column(db.String(20), default='belum lunas')
    keterangan = db.Column(db.Text)
    daycare = db.Column(db.Float, default=0) #add new colom
    extend_hour = db.Column(db.Float, default=0)
    excul = db.Column(db.Float, default=0)
    bimbel = db.Column(db.Float, default=0)
    no_nota = db.Column(db.String(50), unique=True)

    siswa = db.relationship('Siswa', backref='pembayaran') #add new colom
    nis = db.Column(db.String(20), db.ForeignKey('siswa.nis'), nullable=False)

    def validate_for_kwitansi(self):
        required_fields = ['no_nota', 'tanggal_bayar', 'jumlah', 'siswa_id']
        for field in required_fields:
            if getattr(self, field) is None:
                raise ValueError(f"Field {field} tidak boleh kosong")
        
        if not self.siswa:
            raise ValueError("Data siswa tidak ditemukan")
        
        if self.jumlah < 0 or (self.daycare or 0) < 0 or (self.extend_hour or 0) < 0 or (self.excul or 0) < 0 or (self.bimbel or 0) < 0:
            raise ValueError("Nilai pembayaran tidak boleh negatif")

    @classmethod
    def search(cls, keyword): # classmethod mendefinisikan keyword untuk fitur pencarian (search) pada halaman Pembayaran
        return cls.query.join(Siswa).filter(
            (Siswa.nama.ilike(f'%{keyword}%')) |
            (cls.bulan.ilike(f'%{keyword}%')) |
            (cls.tahun.ilike(f'%{keyword}%')) |
            (cls.no_nota.ilike(f'%{keyword}%'))
        ).all()

class JenisPembayaran(db.Model): #new table
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    harga = db.Column(db.Float, nullable=False)
    satuan = db.Column(db.String(50))
    keterangan = db.Column(db.Text)


@login_manager.user_loader # Fungsi untuk memuat user saat login
def load_user(user_id): # Mengambil user berdasarkan ID yang diberikan dari database (SQLAlchemy)
    return User.query.get(int(user_id)) # Mengambil user berdasarkan ID yang diberikan dari database (SQLAlchemy)

# Buat database
with app.app_context(): # Fungsi untuk mengatur konteks aplikasi saat ini untuk operasi database (SQLAlchemy)
    db.create_all() # Membuat semua tabel yang belum ada dalam database (SQLAlchemy)
    # Buat admin default jika belum ada
    if not User.query.filter_by(username='admin').first(): # Jika tidak ada user dengan username 'admin'
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8') # Enkripsi password
        admin = User(username='admin', password=hashed_password, nama_lengkap='Admin', level='admin') # Membuat user admin
        db.session.add(admin) # Menambahkan user admin ke database
        db.session.commit() # Menyimpan perubahan ke database

#########Endline_Model Database#########

############Route################

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # Jika pengguna sudah login
        return redirect(url_for('dashboard')) # Alihkan ke halaman dashboard
    
    if request.method == 'POST': # Jika metode request adalah POST
        username = request.form.get('username') # Ambil username dari form
        password = request.form.get('password') # Ambil password dari form
        user = User.query.filter_by(username=username).first() # Cari user berdasarkan username

        if user and bcrypt.check_password_hash(user.password, password): # Jika user ditemukan dan password cocok
            login_user(user) # Login user melalui LoginManager (Flask-Login)
            return redirect(url_for('dashboard')) # Alihkan ke halaman dashboard
        else: # Jika login gagal
            flash('Login gagal. Periksa username dan password!', 'danger') # Tampilkan pesan error
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user() # Logout user melalui LoginManager (Flask-Login)
    return redirect(url_for('login')) # Alihkan ke halaman login

# Route Admin
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.level != 'admin': # Jika user bukan admin
        return redirect(url_for('logout')) # Alihkan ke logout
    
    total_siswa = Siswa.query.count() # Hitung jumlah siswa
    total_pembayaran = Pembayaran.query.count() # Hitung jumlah pembayaran
    total_spp = SPP.query.count() # Hitung jumlah SPP
    
    return render_template('dashboard.html',
                           total_siswa=total_siswa,
                           total_pembayaran=total_pembayaran,
                           total_spp=total_spp) # Render halaman dashboard

# Route Manajemen Siswa
@app.route('/siswa')
@login_required
#def siswa(): # Fungsi untuk menampilkan halaman manajemen siswa
    #if current_user.level != 'admin': # Jika user bukan admin
        #return redirect(url_for('logout')) # Alihkan ke logout
    
    #data_siswa = Siswa.query.all() # Ambil semua data siswa
    #return render_template('siswa.html', siswa=data_siswa) # Render halaman manajemen siswa
def siswa():
    if current_user.level != 'admin': # Jika user bukan admin
        return redirect(url_for('logout')) # Alihkan ke logout

    keyword = request.args.get('search', '')
    if keyword:
        data_siswa = Siswa.search(keyword)
    else:
        data_siswa = Siswa.query.all()
    return render_template('siswa.html', siswa=data_siswa, keyword=keyword)

@app.route('/siswa/tambah', methods=['GET', 'POST']) # Fungsi untuk menambahkan siswa
@login_required
def tambah_siswa(): # Fungsi untuk menambahkan siswa
    if current_user.level != 'admin': # Jika user bukan admin
        return redirect(url_for('logout')) # Alihkan ke logout
    
    if request.method == 'POST': # Jika metode request adalah POST
        nis = request.form.get('nis') # Ambil NIS dari form
        nama = request.form.get('nama')
        jenis_kelamin = request.form.get('jenis_kelamin')
        tanggal_lahir = request.form.get('tanggal_lahir')
        alamat = request.form.get('alamat')
        
        kelas_id = request.form.get('kelas_id')

        siswa_baru = Siswa(nis=nis, nama=nama,
                           jenis_kelamin=jenis_kelamin,
                           tanggal_lahir=tanggal_lahir,
                           alamat=alamat,
                           kelas_id=kelas_id if kelas_id else None
                           ) # Membuat objek Siswa baru
        
        db.session.add(siswa_baru) # Menambahkan objek Siswa baru ke database
        db.session.commit() # Menyimpan perubahan ke database
        flash('Data siswa berhasil ditambahkan', 'success') # Tampilkan pesan sukses
        return redirect(url_for('siswa')) # Alihkan ke halaman manajemen siswa
    
    kelas_list = Kelas.query.all()
    return render_template('tambah_siswa.html', kelas=kelas_list) # Render halaman tambah siswa 

@app.route('/siswa/edit/<nis>', methods=['GET', 'POST'])
@login_required
def edit_siswa(nis): # Fungsi Edit Siswa
    if current_user.level != 'admin':
        return redirect(url_for('logout'))
    
    siswa = Siswa.query.get_or_404(nis)
    
    if request.method == 'POST':
        siswa.nama = request.form.get('nama')
        siswa.jenis_kelamin = request.form.get('jenis_kelamin')
        siswa.tanggal_lahir = request.form.get('tanggal_lahir')
        siswa.alamat = request.form.get('alamat')
        siswa.status = request.form.get('status')

        siswa.kelas_id = request.form.get('kelas_id')

        db.session.commit()
        flash('Data siswa berhasil diperbarui', 'success')
        return redirect(url_for('siswa'))
    
    kelas_list = Kelas.query.all()
    return render_template('edit_siswa.html', siswa=siswa, kelas=kelas_list)

@app.route('/siswa/hapus/<nis>', methods=['POST'])
@login_required
def hapus_siswa(nis): # Fungsi Hapus Siswa
    if current_user.level != 'admin':
        return redirect(url_for('logout'))
    
    siswa = Siswa.query.get_or_404(nis)
    
    # Cek apakah siswa memiliki pembayaran
    if Pembayaran.query.filter_by(nis=nis).count() > 0:
        flash('Tidak dapat menghapus siswa karena sudah memiliki riwayat pembayaran', 'danger')
        return redirect(url_for('siswa'))
    
    db.session.delete(siswa)
    db.session.commit()
    flash('Data siswa berhasil dihapus', 'success')
    return redirect(url_for('siswa'))

# Route Manajemen SPP
@app.route('/spp') # Fungsi untuk menampilkan halaman manajemen SPP
@login_required
#def spp(): # Fungsi untuk menampilkan halaman manajemen SPP
    #if current_user.level != 'admin': # Jika user bukan admin
        #return redirect(url_for('logout')) # Alihkan ke logout
    
    #data_spp = SPP.query.all() # Ambil semua data SPP
    #return render_template('spp.html', spp=data_spp) # Render halaman manajemen SPP
def spp():
    if current_user.level != 'admin': # Jika user bukan admin
        return redirect(url_for('logout')) # Alihkan ke logout
    
    keyword = request.args.get('search', '')
    if keyword:
        data_spp = SPP.search(keyword)
    else:
        data_spp = SPP.query.all()
    return render_template('spp.html', spp=data_spp, keyword=keyword)

@app.route('/spp/tambah', methods=['GET', 'POST']) # Fungsi untuk menambahkan SPP
@login_required
def tambah_spp():
    if current_user.level != 'admin': # Jika user bukan admin
        return redirect(url_for('logout')) # Alihkan ke logout
    
    if request.method == 'POST': # Jika metode request adalah POST
        tahun_ajaran = request.form.get('tahun_ajaran') # Ambil tahun ajaran dari form
        nominal = float(request.form.get('nominal')) # Ambil nominal SPP dari form
        keterangan = request.form.get('keterangan') # Ambil keterangan SPP dari form
        
        spp_baru = SPP(tahun_ajaran=tahun_ajaran, nominal=nominal, keterangan=keterangan) # Membuat objek SPP baru
        db.session.add(spp_baru) # Menambahkan objek SPP baru ke database
        db.session.commit() # Menyimpan perubahan ke database
        flash('Data SPP berhasil ditambahkan', 'success') # Tampilkan pesan sukses
        return redirect(url_for('spp')) # Alihkan ke halaman manajemen SPP
    
    return render_template('tambah_spp.html') # Render halaman tambah SPP


@app.route('/spp/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_spp(id): # Fungsi Edit SPP
    if current_user.level != 'admin':
        return redirect(url_for('logout'))
    
    spp = SPP.query.get_or_404(id)
    
    if request.method == 'POST':
        spp.tahun_ajaran = request.form.get('tahun_ajaran')
        spp.nominal = float(request.form.get('nominal'))
        spp.keterangan = request.form.get('keterangan')
        
        db.session.commit()
        flash('Data SPP berhasil diperbarui', 'success')
        return redirect(url_for('spp'))
    
    return render_template('edit_spp.html', spp=spp)


@app.route('/spp/hapus/<int:id>', methods=['POST'])
@login_required
def hapus_spp(id): # Fungsi Hapus SPP
    if current_user.level != 'admin':
        return redirect(url_for('logout'))
    
    spp = SPP.query.get_or_404(id)
    
    # Cek apakah SPP memiliki pembayaran
    if Pembayaran.query.filter_by(id_spp=id).count() > 0:
        flash('Tidak dapat menghapus SPP karena sudah digunakan dalam pembayaran', 'danger')
        return redirect(url_for('spp'))
    
    db.session.delete(spp)
    db.session.commit()
    flash('Data SPP berhasil dihapus', 'success')
    return redirect(url_for('spp'))

# Route Pembayaran
@app.route('/pembayaran') # Fungsi untuk menampilkan halaman manajemen pembayaran
@login_required
#def pembayaran():
    #if current_user.level != 'admin': # Jika user bukan admin
        #return redirect(url_for('logout')) # Alihkan ke logout
    
    #data_pembayaran = Pembayaran.query.all() # Ambil semua data pembayaran
    #return render_template('pembayaran.html', pembayaran=data_pembayaran) # Render halaman manajemen pembayaran
def pembayaran():
    if current_user.level != 'admin': # Jika user bukan admin
        return redirect(url_for('logout')) # Alihkan ke logout

    keyword = request.args.get('search', '')
    if keyword:
        data_pembayaran = Pembayaran.search(keyword)
    else:
        data_pembayaran = Pembayaran.query.all()
    return render_template('pembayaran.html', pembayaran=data_pembayaran, keyword=keyword)

@app.route('/pembayaran/tambah', methods=['GET', 'POST']) # Fungsi untuk menambahkan pembayaran
@login_required
def tambah_pembayaran(): # Fungsi untuk menambahkan pembayaran
    if current_user.level != 'admin': # Jika user bukan admin
        return redirect(url_for('logout')) # Alihkan ke logout
    
    if request.method == 'POST': # Jika metode request adalah POST
        nis = request.form.get('nis') # Ambil NIS dari form
        id_spp = request.form.get('id_spp')
        bulan = request.form.get('bulan')
        tahun = request.form.get('tahun')
        #tanggal_bayar = datetime.strptime(request.form.get('tanggal_bayar'), '%Y-%m-%d').date()
        tanggal_bayar = datetime.strptime(request.form.get('tanggal_bayar'), '%Y-%m-%d').date()
        #tanggal_bayar = request.form.get('tanggal_bayar')
        jumlah = float(request.form.get('jumlah'))
        metode_pembayaran = request.form.get('metode_pembayaran')
        status = request.form.get('status')
        keterangan = request.form.get('keterangan')
        ##add new
        daycare = float(request.form.get('daycare', 0))
        extend_hour = float(request.form.get('extend_hour', 0))
        excul = float(request.form.get('excul', 0))
        bimbel = float(request.form.get('bimbel', 0))

        total = jumlah + daycare + extend_hour + excul + bimbel
        no_nota = generate_no_nota(bulan, tahun)
        
        pembayaran_baru = Pembayaran(
            nis=nis, id_spp=id_spp, bulan=bulan, tahun=tahun,
            tanggal_bayar=tanggal_bayar, jumlah=jumlah,
            metode_pembayaran=metode_pembayaran, status=status,
            keterangan=keterangan,

            daycare=daycare,
            extend_hour=extend_hour,
            excul=excul,
            bimbel=bimbel,
            no_nota=no_nota

        ) # Membuat objek pembayaran baru
        db.session.add(pembayaran_baru) # Menambahkan objek pembayaran baru ke database
        db.session.commit() # Menyimpan perubahan ke database
        flash('Pembayaran berhasil dicatat', 'success') # Tampilkan pesan sukses
        return redirect(url_for('pembayaran')) # Alihkan ke halaman manajemen pembayaran
    
    siswa = Siswa.query.all() # Ambil semua data siswa
    spp = SPP.query.all() # Ambil semua data SPP
    return render_template('tambah_pembayaran.html', siswa=siswa, spp=spp) # Render halaman tambah pembayaran

@app.route('/pembayaran/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_pembayaran(id):
    if current_user.level != 'admin':
        return redirect(url_for('logout'))
    
    pembayaran = Pembayaran.query.get_or_404(id)
    siswa_list = Siswa.query.all()
    spp_list = SPP.query.all()
    
    if request.method == 'POST':
        # Update data utama
        pembayaran.nis = request.form.get('nis')
        pembayaran.id_spp = request.form.get('id_spp')
        pembayaran.bulan = request.form.get('bulan')
        pembayaran.tahun = request.form.get('tahun')
        #pembayaran.tanggal_bayar = request.form.get('tanggal_bayar')
        pembayaran.tanggal_bayar = datetime.strptime(request.form.get('tanggal_bayar'), '%Y-%m-%d').date()
        pembayaran.jumlah = float(request.form.get('jumlah', 0))
        pembayaran.metode_pembayaran = request.form.get('metode_pembayaran')
        pembayaran.status = request.form.get('status')
        pembayaran.keterangan = request.form.get('keterangan')
        
        # Update pembayaran tambahan
        pembayaran.daycare = float(request.form.get('daycare', 0))
        pembayaran.extend_hour = float(request.form.get('extend_hour', 0))
        pembayaran.excul = float(request.form.get('excul', 0))
        pembayaran.bimbel = float(request.form.get('bimbel', 0))
        
        # Generate nomor nota baru jika bulan/tahun berubah
        if pembayaran.bulan != request.form.get('bulan') or pembayaran.tahun != request.form.get('tahun'):
            pembayaran.no_nota = generate_no_nota(pembayaran.bulan, pembayaran.tahun)

        if pembayaran.daycare < 0 or pembayaran.extend_hour < 0 or pembayaran.excul < 0 or pembayaran.bimbel < 0:
            flash('Nilai pembayaran tambahan tidak boleh negatif', 'danger')
            return redirect(url_for('edit_pembayaran', id=id))
        
        if pembayaran.jumlah <= -1:
            flash('Nominal SPP pokok harus lebih dari -1', 'danger')
            return redirect(url_for('edit_pembayaran', id=id))

        db.session.commit()
        flash('Data pembayaran berhasil diperbarui', 'success')
        return redirect(url_for('pembayaran'))
    
    return render_template('edit_pembayaran.html',
                        pembayaran=pembayaran,
                        siswa=siswa_list,
                        spp=spp_list)

@app.route('/pembayaran/hapus/<int:id>', methods=['POST'])
@login_required
def hapus_pembayaran(id): # Fungsi Hapus Pembayaran
    if current_user.level != 'admin':
        return redirect(url_for('logout'))
    
    pembayaran = Pembayaran.query.get_or_404(id)
    db.session.delete(pembayaran)
    db.session.commit()
    flash('Data pembayaran berhasil dihapus', 'success')
    return redirect(url_for('pembayaran'))



# Route Kelas 
@app.route('/kelas')
@login_required
#def kelas(): #Kelas - List
    #data_kelas = Kelas.query.all()
    # Hitung jumlah siswa untuk setiap kelas
    #for k in data_kelas:
        #k.jumlah_siswa = len(k.siswa_list)  # atau k.siswa_collection.count()
    #return render_template('kelas.html', kelas=data_kelas)
def kelas():
    if current_user.level != 'admin': # Jika user bukan admin
        return redirect(url_for('logout')) # Alihkan ke logout
    
    keyword = request.args.get('search', '')
    if keyword:
        data_kelas = Kelas.search(keyword)
    else:
        data_kelas = Kelas.query.all()
    # Hitung jumlah siswa
    for k in data_kelas:
        k.jumlah_siswa = len(k.siswa_list)
    return render_template('kelas.html', kelas=data_kelas, keyword=keyword)

@app.route('/kelas/tambah', methods=['GET', 'POST'])
@login_required
def tambah_kelas(): # Kelas - Tambah
    if current_user.level != 'admin':
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        nama = request.form.get('nama_kelas')
        tingkat = request.form.get('tingkat')
        wali = request.form.get('wali_kelas')
        keterangan = request.form.get('keterangan')
        
        kelas_baru = Kelas(
            nama_kelas=nama,
            tingkat=tingkat,
            wali_kelas=wali,
            keterangan=keterangan
        )
        db.session.add(kelas_baru)
        db.session.commit()
        flash('Kelas berhasil ditambahkan', 'success')
        return redirect(url_for('kelas'))
    
    return render_template('tambah_kelas.html')


@app.route('/kelas/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_kelas(id): # Kelas - Edit
    if current_user.level != 'admin':
        return redirect(url_for('logout'))
    
    kelas = Kelas.query.get_or_404(id)
    
    if request.method == 'POST':
        kelas.nama_kelas = request.form.get('nama_kelas')
        kelas.tingkat = request.form.get('tingkat')
        kelas.wali_kelas = request.form.get('wali_kelas')
        kelas.keterangan = request.form.get('keterangan')
        
        db.session.commit()
        flash('Data kelas berhasil diperbarui', 'success')
        return redirect(url_for('kelas'))
    
    return render_template('edit_kelas.html', kelas=kelas)


@app.route('/kelas/hapus/<int:id>', methods=['POST'])
def hapus_kelas(id): # Kelas - Hapus
    kelas = Kelas.query.get_or_404(id)
    
    # Cek menggunakan len() bukan count()
    if len(kelas.siswa_list) > 0:
        flash('Tidak dapat menghapus kelas karena masih memiliki siswa', 'danger')
        return redirect(url_for('kelas'))
    
    db.session.delete(kelas)
    db.session.commit()
    flash('Kelas berhasil dihapus', 'success')
    return redirect(url_for('kelas'))


#Route Cetak Kwitansi
@app.route('/kwitansi/<int:id>')
@login_required
def cetak_kwitansi(id):
    
    pembayaran = Pembayaran.query.get_or_404(id)
    kelas_siswa = pembayaran.siswa.kelas.nama_kelas if pembayaran.siswa.kelas else '-'

    total = (
        pembayaran.jumlah + 
        pembayaran.daycare + 
        pembayaran.extend_hour + 
        pembayaran.excul + 
        pembayaran.bimbel
    )
    
    return render_template('kwitansi.html',
                        pembayaran=pembayaran,
                        kelas_siswa=kelas_siswa,
                        terbilang=angka_ke_terbilang(total),
                        tanggal_sekarang=datetime.now())

############Endline_Route################

############Fungsi Lain##################

def generate_no_nota(bulan, tahun):
    # Format: KCP.PS.<BULAN>.<TAHUN>.<NOMOR URUT>
    bulan_map = {
        'JANUARI': 'JAN', 'FEBRUARI': 'FEB', 'MARET': 'MAR',
        'APRIL': 'APR', 'MEI': 'MEI', 'JUNI': 'JUN',
        'JULI': 'JUL', 'AGUSTUS': 'AUG', 'SEPTEMBER': 'SEP',
        'OKTOBER': 'OCT', 'NOVEMBER': 'NOV', 'DESEMBER': 'DEC'
    }
    
    bulan_upper = bulan.upper()
    bulan_singkat = bulan_map.get(bulan_upper, bulan_upper[:3])
    tahun_singkat = str(tahun)[-2:]
    
    prefix = f"KCP.PS.{bulan_singkat}.{tahun_singkat}."
    
    # Cari nomor urut terakhir
    last_nota = Pembayaran.query.filter(
        Pembayaran.no_nota.like(f"{prefix}%")
    ).order_by(Pembayaran.no_nota.desc()).first()
    
    if last_nota:
        last_num = int(last_nota.no_nota.split('.')[-1])
        return f"{prefix}{last_num + 1:03d}"
    return f"{prefix}001"

def angka_ke_terbilang(n):
    satuan = ['', 'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']
    belasan = ['sepuluh', 'sebelas', 'dua belas', 'tiga belas', 'empat belas', 
              'lima belas', 'enam belas', 'tujuh belas', 'delapan belas', 'sembilan belas']
    puluhan = ['', '', 'dua puluh', 'tiga puluh', 'empat puluh', 
              'lima puluh', 'enam puluh', 'tujuh puluh', 'delapan puluh', 'sembilan puluh']
    
    n = int(n)
    if n == 0:
        return 'nol'
    elif n < 10:
        return satuan[n]
    elif 10 <= n < 20:
        return belasan[n-10]
    elif 20 <= n < 100:
        return puluhan[n//10] + (' ' + satuan[n%10] if n%10 != 0 else '')
    elif 100 <= n < 200:
        return 'seratus ' + angka_ke_terbilang(n%100)
    elif 200 <= n < 1000:
        return satuan[n//100] + ' ratus ' + angka_ke_terbilang(n%100)
    elif 1000 <= n < 2000:
        return 'seribu ' + angka_ke_terbilang(n%1000)
    elif 2000 <= n < 1000000:
        return angka_ke_terbilang(n//1000) + ' ribu ' + angka_ke_terbilang(n%1000)
    elif 1000000 <= n < 1000000000:
        return angka_ke_terbilang(n//1000000) + ' juta ' + angka_ke_terbilang(n%1000000)
    else:
        return 'angka terlalu besar'

############Fungsi Lain##################

if __name__ == '__main__': # Jika script dijalankan secara langsung
    app.run(debug=True) # Jalankan aplikasi dalam mode debug
