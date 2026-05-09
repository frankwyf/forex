from django.db import models

# Create model for historical data from yahoo finance
class HistoricalData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    
    def __str__(self):
        return self.symbol
    
class RecentData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    
    def __str__(self):
        return self.symbol