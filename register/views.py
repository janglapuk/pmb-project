from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.middleware.csrf import rotate_token

from .models import *
from .forms import *

import json as simplejson
import hashlib
import os
import datetime

# Create your views here.


def beranda(request):
    resp = {}

    if request.user.is_authenticated():
        resp['username'] = request.user.username
        resp['authed'] = True

    if request.method == 'GET':
        return render(request, 'register/beranda.html', resp)


def pmb(request):
    resp = {}

    resp['db_agama'] = Agama.objects.all().order_by('id')
    resp['db_prodi'] = ProgramStudi.objects.all().order_by('id')
    resp['db_jenjang'] = JenjangStudi.objects.all().order_by('id')


    if request.user.is_authenticated():
        resp['username'] = request.user.username
        resp['authed'] = True

    if request.method == 'GET':
        rotate_token(request)
        return render(request, 'register/pmb.html', resp)


def pmb_submit(request):
    if request.method == 'POST':

        try:
            token = request.POST.get('csrfmiddlewaretoken')
            if Pendaftar.objects.filter(token=token).count() > 0:
                raise Exception('Form duplicated!')

            nama = request.POST.get('nama')
            alamat = request.POST.get('alamat')
            kota = request.POST.get('kota')
            provinsi = request.POST.get('provinsi')
            identitas = request.POST.get('identitas')
            jenkel = request.POST.get('jenkel')
            pilih_agama = request.POST.get('pilih-agama')
            tempat_lahir = request.POST.get('tempat-lahir')
            tgl_lahir = request.POST.get('tgl-lahir')
            pilih_goldar = request.POST.get('pilih-goldar')
            nomor_telp = request.POST.get('nomor-telp')
            nomor_hp = request.POST.get('nomor-hp')
            email = request.POST.get('email')

            ortu_nama_ayah = request.POST.get('ortu-nama-ayah')
            ortu_nama_ibu = request.POST.get('ortu-nama-ibu')
            ortu_nama_wali = request.POST.get('ortu-nama-wali')
            ortu_alamat = request.POST.get('ortu-alamat')
            ortu_pekerjaan = request.POST.get('ortu-pekerjaan')
            ortu_telepon = request.POST.get('ortu-telepon')
            ortu_email = request.POST.get('ortu-email')

            pend_akhir = request.POST.get('pend-akhir')
            pend_nama_sekolah = request.POST.get('pend-nama-sekolah')
            pend_alamat = request.POST.get('pend-alamat')
            pend_kota_sekolah = request.POST.get('pend-kota-sekolah')
            pend_prov_sekolah = request.POST.get('pend-prov-sekolah')
            pend_jurusan = request.POST.get('pend-jurusan')
            pend_tahun_lulus = request.POST.get('pend-tahun-lulus')
            pend_no_ijazah = request.POST.get('pend-no-ijazah')

            #rencana_jenjang = request.POST.get('rencana-jenjang')
            rencana_prodi = request.POST.get('rencana-prodi')
            rencana_kelas = request.POST.get('rencana-kelas')

            agama = Agama.objects.get(id=int(pilih_agama))
            prodi = ProgramStudi.objects.get(id=int(rencana_prodi))
            kelas = KelasProdi.objects.get(id=int(rencana_kelas))

            pendaftar = Pendaftar(nama=nama, alamat=alamat, kota=kota, provinsi=provinsi, no_ident=identitas,
                                  jenkel=jenkel, agama=agama, tmp_lahir=tempat_lahir, tgl_lahir=tgl_lahir,
                                  gol_dar=pilih_goldar, telepon=nomor_telp, hp=nomor_hp, email=email,
                                  nama_ayah=ortu_nama_ayah, nama_ibu=ortu_nama_ibu, nama_wali=ortu_nama_wali,
                                  alamat_ortu=ortu_alamat, pekerjaan_ortu=ortu_pekerjaan, telepon_ortu=ortu_telepon,
                                  email_ortu=ortu_email, pend_terakhir=pend_akhir, nama_sekolah=pend_nama_sekolah,
                                  alamat_sekolah=pend_alamat, kota_sekolah=pend_kota_sekolah,
                                  provinsi_sekolah=pend_prov_sekolah, jurusan=pend_jurusan,
                                  lulusan_tahun=pend_tahun_lulus, no_ijazah=pend_no_ijazah, rencana_prodi=prodi,
                                  kelas_prodi=kelas, token=token)

            pendaftar.save()

            kode_verifikasi = hashlib.sha1(token + str(pendaftar.pk) + str(datetime.datetime.now())).hexdigest()
            status = Verifikasi(pendaftar=pendaftar,
                                status=0,
                                kode_verifikasi=kode_verifikasi)
            status.save()

        except Exception, e:
            print('Error: ' + e.message)
            return HttpResponseRedirect(reverse('reg_pmb', ), {'submit_error': True})

        return HttpResponseRedirect(reverse('reg_pmb_success', kwargs={'kv': kode_verifikasi[:8].upper()}))

    return HttpResponseRedirect(reverse('reg_pmb'))


def pmb_success(request, kv):
    return render(request, 'register/pmb_success.html', {'kv': kv})

def pmb_json(request, data_key, data_id):
    data = {'error': True, 'message': 'Tidak dapat memproses data atau data tidak tersedia.'}
    json_data = ''

    try:
        if data_key == 'prodi':
            # cari berdasarkan ID prodi
            ps = ProgramStudi.objects.filter(jenjang_id=int(data_id))

            #print(ps)

            if ps and ps.count() > 0:
                prodi = {}

                for p in ps:
                    prodi[p.id] = p.nama

                data['data'] = prodi
                data['error'] = False
                data['message'] = ''

        elif data_key == 'kelas':
            kls = KelasProdi.objects.filter(prodi=int(data_id))

            if kls and kls.count() > 0:
                kelas = {}
                for k in kls:
                    kelas[k.id] = k.kelas.nama

                data['data'] = kelas
                data['error'] = False
                data['message'] = ''

        else:
            data['message'] = ''

            if data_key == 'check_identitas':
                data['error'] = Pendaftar.objects.filter(no_ident=str(data_id)).count() > 0
                if data['error']:
                    data['message'] = 'Identitas "' + str(data_id) + '" sudah ada dalam database.'

            elif data_key == 'check_email':
                data['error'] = Pendaftar.objects.filter(email=str(data_id)).count() > 0
                if data['error']:
                    data['message'] = 'E-mail "' + str(data_id) + '" sudah ada dalam database.'

            elif data_key == 'check_ijazah':
                data['error'] = Pendaftar.objects.filter(no_ijazah=str(data_id)).count() > 0
                if data['error']:
                    data['message'] = 'Nomor ijazah "' + str(data_id) + '" sudah ada dalam database.'

            elif data_key == 'check_kv':
                data['error'] = not (Verifikasi.objects.filter(kode_verifikasi__contains=str(data_id)).count() > 0)
                if data['error']:
                    data['message'] = 'Kode verifikasi "' + str(data_id) + '" tidak ada dalam database.'

            elif data_key == 'check_kv_reg':
                data['error'] = Pembayaran.objects.filter(pendaftar__kode_verifikasi__contains=str(data_id)).count() > 0
                if data['error']:
                    data['message'] = 'Kode verifikasi "' + str(data_id) + '" sudah ada dalam database.'

    except Exception, e:
        data.clear()
        data['error'] = True
        data['message'] = e.message

    finally:
        json_data = simplejson.dumps(data)

    return HttpResponse(json_data, content_type='application/json')


def user_login(request):
    resp = {}
    username = password = ''

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['authed'] = True
                resp['username'] = user
                resp['login_error'] = False
                return HttpResponseRedirect(reverse('reg_beranda'))
            else:
                resp['authed'] = False
                resp['login_error'] = True
        else:
            resp['authed'] = False
            resp['login_error'] = True

        return render(request, 'register/login.html', resp)

    elif request.method == 'GET':
        if request.user.is_authenticated():
            resp['username'] = request.user.username
            resp['authed'] = True
            return HttpResponseRedirect(reverse('reg_beranda'))

        return render(request, 'register/login.html', resp)


def user_logout(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            logout(request)

    return HttpResponseRedirect(reverse('reg_login'))


def verify(request):
    if request.method == 'GET':
        return render(request, 'register/verify.html', {})

    elif request.method == 'POST':
        resp = {'found': False, 'pembayaran': False}

        kv = request.POST.get('kv')

        verifikasi = Verifikasi.objects.filter(kode_verifikasi__contains=kv)
        if verifikasi is not None:
            verifikasi = verifikasi[0]

            resp['found'] = True

            pembayaran = Pembayaran.objects.filter(pendaftar=verifikasi)
            if pembayaran is not None:
                pembayaran = pembayaran[0]

                pemb_status = pembayaran.status

                resp['pembayaran'] = True
                resp['pembayaran_status'] = pemb_status

            resp['pendaftar'] = {'kv': kv,
                                 'nama': verifikasi.pendaftar.nama,
                                 'tanggal': verifikasi.pendaftar.wkt_daftar,
                                 'jenjang': verifikasi.pendaftar.rencana_prodi.jenjang,
                                 'prodi': verifikasi.pendaftar.rencana_prodi.nama,
                                 'kelas': verifikasi.pendaftar.kelas_prodi.kelas.nama,
                                 }

            resp['verifikasi'] = verifikasi.status

        return render(request, 'register/verify.html', resp)

    return HttpResponseRedirect(reverse('reg_verify'))


def confirm(request):
    resp = {}

    if request.method == 'GET':
        banks = Pengaturan.objects.filter(kategori='BANK')
        resp['banks'] = banks

        if request.GET.get('error') == str(1):
            resp['error'] = True

            message = request.GET.get('msg')
            resp['error_message'] = 'Terjadi kesalahan proses data: ' + str(message)

            if request.GET.get('msg') == 'duplicate_data':
                resp['error_message'] = 'Terjadi duplikasi data, silakan periksa data dan ulangi!'

            elif request.GET.get('msg') == 'invalid_extension':
                resp['error_message'] = 'Gambar yang anda unggah harus berformat JPG/GIF/PNG.'

        return render(request, 'register/confirm.html', resp)

    return render(request, 'register/confirm.html', resp)


def confirm_submit(request, key_id):
    print request.POST

    if request.method == 'POST':
        try:
            if key_id == 'transfer':
                rektujuan = request.POST.get('rektujuan')
                kv = request.POST.get('kv')
                pengirim = request.POST.get('pengirim')
                norek = request.POST.get('norek')
                bank = request.POST.get('bank')
                cabang = request.POST.get('cabang')
                nominal = request.POST.get('nominal')

                obj_sp = Verifikasi.objects.filter(kode_verifikasi__contains=kv)[0]
                obj_rektujuan = Pengaturan.objects.get(id=int(rektujuan))

                pembayaran = Pembayaran(pendaftar=obj_sp,
                                        rekening_tujuan=obj_rektujuan,
                                        metode_bayar=1,
                                        pengirim=pengirim,
                                        norek=norek,
                                        bank=bank,
                                        cabang=cabang,
                                        nominal=int(nominal))

                pembayaran.save()

                return HttpResponseRedirect(reverse('reg_confirm_success'))

            elif key_id == 'ibank':
                rektujuan2 = request.POST.get('rektujuan2')
                kv2 = request.POST.get('kv2')
                norek2 = request.POST.get('norek2')
                bank2 = request.POST.get('bank2')

                ext = os.path.splitext(request.FILES['buktitrf'])
                ext = ext[1].lower()
                print ext
                if ext != '.jpg' or ext != '.gif' or ext != '.png':
                    raise Exception('invalid_extension')

                if Pembayaran.objects.filter(pendaftar__kode_verifikasi__contains=kv2.lower()).count() > 0:
                    raise Exception('duplicate_data')

                obj_sp = Verifikasi.objects.filter(kode_verifikasi__contains=kv2.lower())[0]
                obj_rektujuan = Pengaturan.objects.get(id=int(rektujuan2))

                form = PembayaranForm(request.POST, request.FILES)
                if form.is_valid():
                    pembayaran = Pembayaran(pendaftar=obj_sp,
                                            rekening_tujuan=obj_rektujuan,
                                            metode_bayar=2,
                                            pengirim='N/A',
                                            norek=norek2,
                                            bank=bank2,
                                            cabang='N/A',
                                            nominal=0,
                                            bukti_transfer=form.cleaned_data['buktitrf']
                                            )
                    pembayaran.save()

                return HttpResponseRedirect(reverse('reg_confirm_success'))

        except Exception, e:
            print('Exception: ' + e.message)
            return HttpResponseRedirect(reverse('reg_confirm') + '?error=1&msg=' + e.message)

    return render(request, 'register/confirm.html', {})

def confirm_success(request):
    return render(request, 'register/confirm_success.html', {})