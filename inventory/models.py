from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
      ordering = ["id"]
      
    def __str__(self):
        return self.name
      
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    
    class Meta:
      ordering = ["id"]
      
    def __str__(self):
        return self.name
