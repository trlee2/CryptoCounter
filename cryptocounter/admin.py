from django.contrib import admin

from .models import Coin, Ico, Price, WatchItem

# Register your models here.
admin.site.register(Coin)
admin.site.register(Ico)
# DELETE BELOW
admin.site.register(Price)
admin.site.register(WatchItem)
