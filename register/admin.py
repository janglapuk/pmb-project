from django.contrib import admin
from .models import *

# Register your models here.


class PendaftarAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'token', 'wkt_daftar',)

class PembayaranAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'tanggal',)

admin.site.register(Agama)
admin.site.register(JenjangStudi)
admin.site.register(Kelas)
admin.site.register(ProgramStudi)
admin.site.register(KelasProdi)
admin.site.register(Pendaftar, PendaftarAdmin)
admin.site.register(Verifikasi)
admin.site.register(Pengaturan)
admin.site.register(Pembayaran, PembayaranAdmin)