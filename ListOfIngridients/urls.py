from django.urls import path
from .views import *

urlpatterns = [
    path("ingridients-categories/", IngridientsCategoryViewset.as_view()),
    path("ingridients-categories/<int:pk>/", IngridientsCategoryViewset.as_view()),
    path("ingridients-item/", IngridientsItemViewset.as_view()),
    path("ingridients-item/<int:pk>/", IngridientsItemViewset.as_view()),
    path("event-ingridient-list/",EventIngridientListViewSet.as_view())
]