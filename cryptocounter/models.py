from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Coin(models.Model):
    coin_id = models.IntegerField(default=0)
    coin_name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=10)
    block_chain = models.CharField(max_length=10)
    search_terms = models.TextField(max_lenght=500)

class Ico(models.Model):
    ico_id = models.IntegerField(default=0)
    ico_name = models.CharField(max_length=200)
    start = models.DateField()
    end = models.DateField()
    description = models.TextField()
    search_terms = models.TextField(max_lenght=500)

class Price(models.Model):
    coin_id = models.ForeignKey(Coin, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.DecimalField(max_digits=20, decimal_places=2)

class SocialCoin(models.Model):
    coin_id = models.ForeignKey(Coin, on_delete=models.CASCADE)
    date = models.DateField()
    num_tweets = models.IntegerField(default=0)
    num_searches = models.IntegerField(default=0)
    num_articles = models.IntegerField(default=0)

class SocialIco(models.Model):
    ico_id = models.ForeignKey(Ico, on_delete=models.CASCADE)
    date = models.DateField()
    num_tweets = models.IntegerField(default=0)
    num_searches = models.IntegerField(default=0)
    num_articles = models.IntegerField(default=0)

class OverallSocial(models.Model):
    date = models.DateField()
    num_tweets = models.IntegerField(default=0)
    num_searches = models.IntegerField(default=0)
    num_articles = models.IntegerField(default=0)

class WatchItem(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    coin_id = models.ForeignKey(Coin, on_delete=models.CASCADE)
    date_added = models.DateField()
