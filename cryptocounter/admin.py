from django.contrib import admin

from .models import Coin, Ico, Price, WatchItem, WatchIco, OverallSocial, SocialCoin

# Register your models here.
admin.site.register(Coin)
admin.site.register(Ico)
# DELETE BELOW
admin.site.register(Price)
admin.site.register(WatchItem)
admin.site.register(WatchIco)
admin.site.register(OverallSocial)
admin.site.register(SocialCoin)
