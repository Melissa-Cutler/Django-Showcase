from django.contrib import admin
from .models import Fund, Commitment, Investment, Call

# Register your models here.

admin.site.register(Fund)
admin.site.register(Commitment)
admin.site.register(Investment)
admin.site.register(Call)


