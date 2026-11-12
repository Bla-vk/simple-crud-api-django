from rest_framework import viewsets

from .models import Item, Location
from .serializers import ItemSerializer, LocationSerializer

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    
class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    
    def get_queryset(self):
        qs = Item.objects.all()
        location = self.request.query_params.get("location")
        if location:
            if not location.isdigit():
                return qs.none()
            qs = qs.filter(location_id=location)
        return qs