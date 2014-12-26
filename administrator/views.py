from django.shortcuts import render
from register.models import *
from django.core.exceptions import *
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
import json as simplejson

from django.contrib.admin.util import NestedObjects
from django.db import DEFAULT_DB_ALIAS

# Create your views here.

# http://thirld.com/blog/2012/09/17/django-enumerate-related-objects-cascade-deleted/
def have_relations_with(obj):
    collector = NestedObjects(using=DEFAULT_DB_ALIAS)
    collector.collect([obj])
    return len(collector.nested()) > 1


def adm_nav_counts():
    retval = {}

    regs = Pendaftar.objects.all()
    unverified = Verifikasi.objects.filter(status=0)
    verified = Verifikasi.objects.filter(status=1)

    payment_all = Pembayaran.objects.all()
    payment_pending = Pembayaran.objects.filter(status=0)
    payment_ok = Pembayaran.objects.filter(status=1)

    retval['reg_all'] = regs.count()
    retval['reg_verified'] = verified.count()
    retval['reg_unverified'] = unverified.count()
    retval['payment_all'] = payment_all.count()
    retval['payment_unconfirmed'] = payment_pending.count()
    retval['payment_confirmed'] = payment_ok.count()

    return retval


def adm_beranda(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adm_login'))

    username = request.user.username
    all_counts = adm_nav_counts()
    resp = {'counts': all_counts, 'username': username}

    return render(request, 'administrator/index.html', resp)

def adm_registrations(request, key_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adm_login'))

    username = request.user.username
    all_counts = adm_nav_counts()

    if key_id == 'all':
        return render(request, 'administrator/registrations/all.html', {'counts': all_counts, 'username': username})

    if key_id == 'verified':
        return render(request, 'administrator/registrations/verified.html', {'counts': all_counts, 'username': username})

    if key_id == 'unverified':
        return render(request, 'administrator/registrations/unverified.html', {'counts': all_counts, 'username': username})

    return render(request, 'administrator/login.html', {})


def adm_payments(request, key_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adm_login'))

    all_counts = adm_nav_counts()
    username = request.user.username

    if key_id == 'all':
        return render(request, 'administrator/payments/all.html', {'counts': all_counts, 'username': username})

    if key_id == 'confirmed':
        return render(request, 'administrator/payments/confirmed.html', {'counts': all_counts, 'username': username})

    if key_id == 'unconfirmed':
        return render(request, 'administrator/payments/unconfirmed.html', {'counts': all_counts, 'username': username})

    return render(request, 'administrator/login.html', {})

def adm_login(request):
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
                return HttpResponseRedirect(reverse('adm_beranda'))
            else:
                resp['authed'] = False
                resp['login_error'] = True
        else:
            resp['username'] = username
            resp['authed'] = False
            resp['login_error'] = True

        return render(request, 'administrator/login.html', resp)

    elif request.method == 'GET':

        if request.user.is_authenticated():
            resp['username'] = request.user.username
            resp['authed'] = True
            return HttpResponseRedirect(reverse('adm_beranda'))

        return render(request, 'administrator/login.html', resp)


def adm_logout(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            logout(request)

    return HttpResponseRedirect(reverse('adm_login'))

### JSON DATA ###
def adm_json(request, key_id):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adm_login'))

    if request.method == 'GET':
        json_data = {}

        if key_id == 'reg_all':
            data = []
            pendaftar = Pendaftar.objects.all().order_by('-wkt_daftar')

            for p in pendaftar:
                status = Verifikasi.objects.get(pendaftar=p)
                local_time = timezone.localtime(p.wkt_daftar).strftime('%Y/%m/%d %H:%M')

                status_bayar = 'Belum'
                if status.status == 1:
                    status_bayar = 'Sudah'

                data.append([p.id,
                            p.nama,
                            status.kode_verifikasi[:8].upper(),
                            p.rencana_prodi.jenjang.nama,
                            p.rencana_prodi.nama,
                            p.kelas_prodi.kelas.nama,
                            str(local_time),
                            status_bayar
                            ])

            json_data['data'] = data

            return HttpResponse(simplejson.dumps(json_data), content_type='application/json')

        elif (key_id == 'reg_verified') or (key_id == 'reg_unverified'):
            data = []
            status = None

            if key_id == 'reg_verified':
                status = Verifikasi.objects.filter(status=1).order_by('-pendaftar__wkt_daftar')
            else:
                status = Verifikasi.objects.filter(status=0).order_by('-pendaftar__wkt_daftar')

            for s in status:
                terbayar = Pembayaran.objects.filter(pendaftar=s.pendaftar, status=1).count() > 0

                local_time = timezone.localtime(s.pendaftar.wkt_daftar).strftime('%Y/%m/%d %H:%M')
                data.append([s.pendaftar.id,
                             terbayar, # aksi
                             s.pendaftar.nama,
                             s.kode_verifikasi[:8].upper(),
                             s.pendaftar.rencana_prodi.jenjang.nama,
                             s.pendaftar.rencana_prodi.nama,
                             s.pendaftar.kelas_prodi.kelas.nama,
                             str(local_time)])

            json_data['data'] = data

            return HttpResponse(simplejson.dumps(json_data), content_type='application/json')

        elif key_id == 'payment_all':
            data = []
            pembayaran = Pembayaran.objects.all().order_by('-tanggal')

            for p in pembayaran:
                status = Verifikasi.objects.get(pendaftar=p)
                rek_tuj = Pengaturan.objects.get(id=p.rekening_tujuan.id)

                status_bayar = 'Belum'
                if p.status == 1:
                    status_bayar = 'Sudah'

                if p.metode_bayar == 1:
                    metode_bayar = 'Transfer'
                elif p.metode_bayar == 2:
                    metode_bayar = 'ATM/iBank'
                else:
                    metode_bayar = 'Office'

                local_time = timezone.localtime(p.tanggal).strftime('%Y/%m/%d %H:%M')
                data.append([p.id,
                             p.status, # aksi
                             status.kode_verifikasi[:8].upper(),
                             metode_bayar,
                             rek_tuj.nama,
                             p.norek,
                             p.pengirim,
                             p.bank,
                             p.cabang,
                             p.nominal,
                             str(local_time),
                             status_bayar
                ])

            json_data['data'] = data

            return HttpResponse(simplejson.dumps(json_data), content_type='application/json')

        elif (key_id == 'payment_confirmed') or (key_id == 'payment_unconfirmed'):
            data = []
            pembayaran = None

            if key_id == 'payment_unconfirmed':
                pembayaran = Pembayaran.objects.filter(status=0).order_by('-tanggal')
            else:
                pembayaran = Pembayaran.objects.filter(status=1).order_by('-tanggal')

            for p in pembayaran:
                status = Verifikasi.objects.get(pendaftar=p)
                rek_tuj = Pengaturan.objects.get(id=p.rekening_tujuan.id)

                if p.metode_bayar == 1:
                    metode_bayar = 'Transfer'
                elif p.metode_bayar == 2:
                    metode_bayar = 'ATM/iBank'
                else:
                    metode_bayar = 'Office'

                local_time = timezone.localtime(p.tanggal).strftime('%Y/%m/%d %H:%M')
                data.append([p.id,
                             p.status, # aksi
                             status.kode_verifikasi[:8].upper(),
                             metode_bayar,
                             rek_tuj.nama,
                             p.norek,
                             p.pengirim,
                             p.bank,
                             p.cabang,
                             p.nominal,
                             str(local_time)
                ])

            json_data['data'] = data

            return HttpResponse(simplejson.dumps(json_data), content_type='application/json')

        elif key_id == 'data_count':
            data = {}

            all_counts = adm_nav_counts()
            print all_counts

            data['reg'] = {'all': all_counts['reg_all'],
                           'verified': all_counts['reg_verified'],
                           'unverified': all_counts['reg_unverified']
            }

            data['payment'] = {'all': all_counts['payment_all'],
                               'confirmed': all_counts['payment_confirmed'],
                               'unconfirmed': all_counts['payment_unconfirmed']
            }

            json_data['data'] = data

            return HttpResponse(simplejson.dumps(json_data), content_type='application/json')

        return HttpResponse(simplejson.dumps({'error': True}), content_type='application/json')

### AJAX REQUEST ###
def adm_ajax(request, action, key_id):
    if not request.user.is_authenticated() :
        return HttpResponseRedirect(reverse('adm_login'))

    data = {'error': True, 'message': 'Error'}

    if request.user.is_superuser:
        try:
            if (action == 'reg_verify') or (action == 'reg_unverify'):
                sp = Verifikasi.objects.get(id=int(key_id))

                if sp is None:
                    raise Exception('Objek dengan ID \''+ key_id + '\' tidak ada')

                sp.status = (action == 'reg_verify')
                sp.save()

                data['error'] = False


            if (action == 'payment_confirm') or (action == 'payment_unconfirm'):
                pembayaran = Pembayaran.objects.get(id=int(key_id))

                if pembayaran is None:
                    raise Exception('Objek dengan ID \'' + key_id + '\' tidak ada')

                # QuerySet berdasarkan field pendaftar (single row)
                sp = Verifikasi.objects.filter(pendaftar=pembayaran.pendaftar)[0]

                if sp is None:
                    raise Exception('Objek dengan ID \'' + key_id + '\' tidak ada')

                # status apakah verified atau unverified
                status = (action == 'payment_confirm')

                pembayaran.status = status
                pembayaran.save()

                # memastikan (revert) status yang sudah 'terverifikasi' menjadi 'belum terverifikasi'
                # jika melakukan 'unconfirm'
                if action == 'payment_unconfirm':
                    sp.status = 0
                    sp.save()

                data['error'] = False

                return HttpResponse(simplejson.dumps(data), content_type='application/json')

        except Exception, e:
            data['message'] = e.message
    else:
        # jika user berjalan sebagai demo (non-admin/superuser)
        data['message'] = 'Error: Tidak memiliki hak akses untuk mengubah data!'

    return HttpResponse(simplejson.dumps(data), content_type='application/json')


def adm_settings_general(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adm_login'))

    resp = {'error': False}

    if request.user.is_superuser:

        if request.method == 'POST':
            print request.POST

            if request.POST.get('action') == 'set-web-title':
                qs_title = Pengaturan.objects.filter(kategori='WEBTITLE')

                if qs_title.exists():
                    qs_title = qs_title[0]
                    qs_title.nama = request.POST.get('webtitle')
                    qs_title.save()
                else:
                    qs_title = Pengaturan(kategori='WEBTITLE',
                                          nama=request.POST.get('webtitle'))
                    qs_title.save()

                return HttpResponseRedirect(reverse('adm_settings_general'))

            elif request.POST.get('action') == 'tambah-agama':
                qs_agama = Agama.objects.filter(nama=request.POST.get('agama'))
                if qs_agama.exists():
                    qs_agama = qs_agama[0]
                    resp['error'] = True
                    resp['error_message'] = 'Entri (' + qs_agama.nama + ') telah ada dalam database'
                else:
                    qs_agama = Agama(nama=request.POST.get('agama'))
                    qs_agama.save()

            elif request.POST.get('action') == 'delete-agama':
                try:
                    qs_agama = Agama.objects.get(pk=int(request.POST.get('data-id')))

                    if have_relations_with(qs_agama):
                        resp['error'] = True
                        resp['error_message'] = 'Entri (' + qs_agama.nama + ') tidak dapat dihapus karena terkait dengan data lainnya.'
                    else:
                        qs_agama.delete()

                except ObjectDoesNotExist:
                    pass

    qs_agama = Agama.objects.all()
    qs_title = Pengaturan.objects.filter(kategori='WEBTITLE')

    webtitle = ''
    if qs_title.count() > 0:
        webtitle = qs_title[0].nama

    username = request.user.username

    resp['counts'] = adm_nav_counts()
    resp['username'] = username
    resp['webtitle'] = webtitle
    resp['agama'] = qs_agama
    resp['csrf_token'] = get_token(request)

    return render(request, 'administrator/settings/general.html', resp)

def adm_settings_academic(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adm_login'))

    resp = {'error': False}

    if request.user.is_superuser:

        if request.method == 'POST':
            print request.POST

            if request.POST.get('action') == 'tambah-kelas':
                post_nama = request.POST.get('kelas-studi')
                qs_kelas = Kelas.objects.filter(nama=post_nama)
                if qs_kelas.exists():
                    resp['error'] = True
                    resp['error_message'] = 'Entri (' + post_nama + ') telah ada dalam database'
                else:
                    qs_kelas = Kelas(nama=post_nama)
                    qs_kelas.save()

                return HttpResponseRedirect(reverse('adm_settings_academic'))

            elif request.POST.get('action') == 'tambah-jenjang':
                post_jenjang = request.POST.get('jenjang-studi')
                qs_jenjang = JenjangStudi.objects.filter(nama=post_jenjang)
                if qs_jenjang.exists():
                    resp['error'] = True
                    resp['error_message'] = 'Entri (' + post_jenjang + ') telah ada dalam database'
                else:
                    qs_jenjang = JenjangStudi(nama=post_jenjang)
                    qs_jenjang.save()

                return HttpResponseRedirect(reverse('adm_settings_academic'))

            elif request.POST.get('action') == 'tambah-prodi':
                duplicated = False
                post_prodi = request.POST.get('nama-prodi')
                post_jenjang = request.POST.get('jenjang-studi')
                qs_prodi = ProgramStudi.objects.filter(nama=post_prodi)
                qs_jenjang = JenjangStudi.objects.get(pk=int(post_jenjang))
                if qs_prodi.exists():
                    for prodi in qs_prodi:
                        duplicated = (prodi.jenjang == qs_jenjang)
                        if duplicated:
                            break

                    if duplicated:
                        resp['error'] = True
                        resp['error_message'] = 'Entri (' + post_prodi + ') dengan jenjang (' + qs_jenjang.nama + ') telah ada dalam database'

                if not duplicated:
                    qs_prodi = ProgramStudi(nama=post_prodi,
                                            jenjang=qs_jenjang)
                    qs_prodi.save()

                #return HttpResponseRedirect(reverse('adm_settings_academic'))

            elif request.POST.get('action') == 'tambah-kelas-prodi':
                duplicated = False
                post_prodi = request.POST.get('program-studi')
                post_kelas = request.POST.get('kelas-studi')

                qs_prodi = ProgramStudi.objects.get(pk=int(post_prodi))
                qs_kelas = Kelas.objects.get(pk=int(post_kelas))

                qs_kelas_prodi = KelasProdi.objects.all()
                for kp in qs_kelas_prodi:
                    if (kp.prodi == qs_prodi) and (kp.kelas == qs_kelas):
                        duplicated = True
                        break

                if duplicated:
                    resp['error'] = True
                    resp['error_message'] = 'Entri (' + qs_prodi.nama + ') dengan kelas (' + qs_kelas.nama + ') telah ada dalam database'
                else:
                    qs_kelas_prodi = KelasProdi(prodi=qs_prodi,
                                                kelas=qs_kelas)
                    qs_kelas_prodi.save()

                #return HttpResponseRedirect(reverse('adm_settings_academic'))

            elif request.POST.get('action') == 'delete-kelas':
                try:
                    qs_kelas = Kelas.objects.get(pk=int(request.POST.get('data-id')))

                    if have_relations_with(qs_kelas):
                        resp['error'] = True
                        resp['error_message'] = 'Entri (' + qs_kelas.nama + ') tidak dapat dihapus karena terkait dengan data lainnya.'
                    else:
                        qs_kelas.delete()

                except ObjectDoesNotExist:
                    pass

            elif request.POST.get('action') == 'delete-jenjang':
                try:
                    qs_jenjang = JenjangStudi.objects.get(pk=int(request.POST.get('data-id')))

                    if have_relations_with(qs_jenjang):
                        resp['error'] = True
                        resp['error_message'] = 'Entri (' + qs_jenjang.nama + ') tidak dapat dihapus karena terkait dengan data lainnya.'
                    else:
                        qs_jenjang.delete()

                except ObjectDoesNotExist:
                    pass

            elif request.POST.get('action') == 'delete-prodi':
                try:
                    qs_prodi = ProgramStudi.objects.get(pk=int(request.POST.get('data-id')))

                    if have_relations_with(qs_prodi):
                        resp['error'] = True
                        resp['error_message'] = 'Entri (' + qs_prodi.nama + ') tidak dapat dihapus karena terkait dengan data lainnya.'
                    else:
                        qs_prodi.delete()

                except ObjectDoesNotExist:
                    pass

            elif request.POST.get('action') == 'delete-kelas-prodi':
                try:
                    qs_kelas_prodi = KelasProdi.objects.get(pk=int(request.POST.get('data-id')))

                    if have_relations_with(qs_kelas_prodi):
                        resp['error'] = True
                        resp['error_message'] = 'Entri (' + qs_kelas_prodi.prodi.nama + ') tidak dapat dihapus karena terkait dengan data lainnya.'
                    else:
                        qs_kelas_prodi.delete()

                except ObjectDoesNotExist:
                    pass

    qs_kelas = Kelas.objects.all()
    if qs_kelas.exists():
        resp['qs_kelas'] = qs_kelas

    qs_jenjang = JenjangStudi.objects.all()
    if qs_jenjang.exists():
        resp['qs_jenjang'] = qs_jenjang

    qs_kelas_prodi = KelasProdi.objects.all()
    if qs_kelas_prodi.exists():
        resp['qs_kelas_prodi'] = qs_kelas_prodi

    qs_prodi = ProgramStudi.objects.all()
    if qs_prodi.exists():
        resp['qs_prodi'] = qs_prodi

    username = request.user.username
    resp['counts'] = adm_nav_counts()
    resp['username'] = username
    resp['csrf_token'] = get_token(request)

    return render(request, 'administrator/settings/academic.html', resp)

def adm_settings_administration(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adm_login'))

    resp = {'error': False}

    if request.user.is_superuser:
        if request.method == 'POST':
            print request.POST

            if request.POST.get('action') == 'addbank':
                bank = Pengaturan(kategori='BANK', nama=request.POST.get('newbank'))
                bank.save()

            elif request.POST.get('action') == 'delbank':
                try:
                    bank = Pengaturan.objects.get(pk=int(request.POST.get('bank-id')))
                    if Pembayaran.objects.filter(rekening_tujuan=bank).exists():
                        resp['error'] = True
                        resp['error_message'] = 'Gagal menghapus karena data yang akan dihapus telah terkait oleh data lainnya.'
                    else:
                        bank.delete()

                except ObjectDoesNotExist, e:
                    resp['error'] = True

    banks = Pengaturan.objects.filter(kategori='BANK')

    username = request.user.username

    resp['counts'] = adm_nav_counts()
    resp['username'] = username
    resp['banks'] = banks
    resp['csrf_token'] = get_token(request)

    return render(request, 'administrator/settings/administration.html', resp)

def adm_settings_users(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('adm_login'))

    username = request.user.username
    all_counts = adm_nav_counts()
    resp = {'counts': all_counts, 'username': username}

    return render(request, 'administrator/settings/users.html', resp)