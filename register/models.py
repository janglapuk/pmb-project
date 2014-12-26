from django.db import models
import datetime
import os

class Agama(models.Model):
    nama = models.CharField(max_length=20)

    def __unicode__(self):
        return self.nama

    class Meta:
        verbose_name_plural = 'Agama'


class JenjangStudi(models.Model):
    nama = models.CharField(max_length=30)

    def __unicode__(self):
        return self.nama

    class Meta:
        verbose_name_plural = 'JenjangStudi'


class ProgramStudi(models.Model):
    nama = models.CharField(max_length=30)
    jenjang = models.ForeignKey(JenjangStudi)

    def __unicode__(self):
        return self.nama

    class Meta:
        verbose_name_plural = 'ProgramStudi'


class Kelas(models.Model):
    nama = models.CharField(max_length=20)

    def __unicode__(self):
        return self.nama

    class Meta:
        verbose_name_plural = 'Kelas'


class KelasProdi(models.Model):
    kelas = models.ForeignKey(Kelas)
    prodi = models.ForeignKey(ProgramStudi)

    def __unicode__(self):
        return unicode(self.kelas) + " (" + unicode(self.prodi) + ")"

    class Meta:
        verbose_name_plural = 'KelasProdi'


class Pendaftar(models.Model):

    JENIS_KELAMIN = (
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    )

    # data pribadi
    nama = models.CharField(max_length=50)
    alamat = models.CharField(max_length=250)
    kota = models.CharField(max_length=30, default='')
    provinsi = models.CharField(max_length=30, default='')
    no_ident = models.CharField(max_length=20)
    jenkel = models.CharField(max_length=1, choices=JENIS_KELAMIN)
    agama = models.ForeignKey(Agama)
    tmp_lahir = models.CharField(max_length=20)
    tgl_lahir = models.DateField()
    gol_dar = models.CharField(max_length=3)
    telepon = models.CharField(max_length=15)
    hp = models.CharField(max_length=15)
    email = models.EmailField(blank=True)

    # data ortu
    nama_ayah = models.CharField(max_length=50)
    nama_ibu = models.CharField(max_length=50)
    nama_wali = models.CharField(max_length=50, blank=True)
    alamat_ortu = models.CharField(max_length=250)
    pekerjaan_ortu = models.CharField(max_length=20)
    telepon_ortu = models.CharField(max_length=15, blank=True)
    email_ortu = models.EmailField(blank=True)

    # data pendidikan
    pend_terakhir = models.CharField(max_length=10)
    nama_sekolah = models.CharField(max_length=50)
    alamat_sekolah = models.CharField(max_length=250)
    kota_sekolah = models.CharField(max_length=30, default='')
    provinsi_sekolah = models.CharField(max_length=30)
    jurusan = models.CharField(max_length=50)
    lulusan_tahun = models.CharField(max_length=4)
    no_ijazah = models.CharField(max_length=50)

    # rencana kuliah
    rencana_prodi = models.ForeignKey(ProgramStudi)
    kelas_prodi = models.ForeignKey(KelasProdi)

    # csrf as unique token
    token = models.CharField(max_length=64, default='')

    # tanggal terdaftar
    wkt_daftar = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.nama + ' (' + unicode(self.rencana_prodi) + ')'

    class Meta:
        verbose_name_plural = 'Pendaftar'


class Verifikasi(models.Model):
    STATUS_VERIFIKASI = (
        (0, 'Belum Terverifikasi'),
        (1, 'Terverifikasi'),
    )
    pendaftar = models.ForeignKey(Pendaftar)
    status = models.IntegerField(default=0, choices=STATUS_VERIFIKASI)
    kode_verifikasi = models.CharField(max_length=40, default='')

    def __unicode__(self):
        return self.kode_verifikasi[:8].upper() + ' - ' + self.pendaftar.nama

    class Meta:
        verbose_name_plural = 'Verifikasi'


class Pengaturan(models.Model):
    kategori = models.CharField(max_length=10, default='')
    nama = models.CharField(max_length=250, default='')

    def __unicode__(self):
        return self.kategori + ' - ' + self.nama

    class Meta:
        verbose_name_plural = 'Pengaturan'


def pembayaran_update_upload_name(instance, filename):
    ext = os.path.splitext(filename)[1]
    if ext == '':
        ext = '.jpg'

    fn = instance.pendaftar.kode_verifikasi + ext.lower()

    return os.path.join('register', 'static', 'upload', 'buktitransfer', fn)


class Pembayaran(models.Model):
    METODE_PEMBAYARAN = (
        (1, 'Transfer'),
        (2, 'ATM/i-Banking'),
        (3, 'Office')
    )

    STATUS_BAYAR = (
        (0, 'Belum dibayar'),
        (1, 'Sudah dibayar'),
    )

    pendaftar = models.ForeignKey(Verifikasi)
    rekening_tujuan = models.ForeignKey(Pengaturan)
    metode_bayar = models.IntegerField(choices=METODE_PEMBAYARAN)
    pengirim = models.CharField(max_length=50)
    norek = models.CharField(max_length=50)
    bank = models.CharField(max_length=50)
    cabang = models.CharField(max_length=50)
    nominal = models.IntegerField()
    status = models.IntegerField(choices=STATUS_BAYAR, default=0)
    tanggal = models.DateTimeField(auto_now_add=True)
    bukti_transfer = models.FileField(upload_to=pembayaran_update_upload_name, default='register/static/upload/nopic.jpg')

    def __unicode__(self):
        return self.pendaftar.kode_verifikasi[:8].upper() + ' - ' + \
               self.pendaftar.pendaftar.nama

    class Meta:
        verbose_name_plural = 'Pembayaran'