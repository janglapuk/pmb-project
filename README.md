Pra-UAS Project
=
Projek ini dibuat untuk keperluan perkuliahan dengan menggunakan Django sebagai _web framework_. Awalnya di-*generate* secara lokal menggunakan ```django-admin```. 

Karena dibutuhkan tampil secara online, maka kami memutuskan untuk menggunakan layanan [Openshift](https://openshift.redhat.com) secara gratis. Openshift memiliki struktur sistem dan _files_ yang berbeda, maka kami adaptasi menggunakan projek [openshift-django17](https://github.com/jfmatth/openshift-django17) agar dapat menggunakan Django versi 1.7 (Python 2.7).

###Cara menggunakan di lingkungan lokal
- **Pastikan** `Python` memiliki versi `2.7.x`
```
$ python --version
```

- **Pastikan** anda telah meng-install Django dengan minimal versi 1.7
- _Clone_ repositori ini
```
$ git clone https://github.com/janglapuk/pmb-project.git
```

- Masuk ke direktori aplikasi utama
```
$ cd pmb/app
```

- Buat [_migrations_](https://docs.djangoproject.com/en/1.7/topics/migrations/) untuk melakukan sinkronisasi dan perubahan pada _models_ ke _database scheme_.
```
$ python manage.py makemigrations
```

- Lakukan proses migrasi
```
$ python manage.py migrate
```

- Sinkronisasi database; otomatis akan diminta membuat sebuah akun `superuser`, lakukan saja
```
$ python manage.py syncdb
```

- Terakhir, jalankan server
```
$ python manage.py runserver
```