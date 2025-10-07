from rest_framework import routers
from .views import CustomUserViewSet

router = routers.SimpleRouter()
router.register(r'', CustomUserViewSet)
urlpatterns = router.urls
