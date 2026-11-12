from rest_framework.routers import DefaultRouter

from .views import ItemViewSet, LocationViewSet

router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'items', ItemViewSet, basename='item')

urlpatterns = router.urls