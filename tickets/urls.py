
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from tickets.views import TicketViewSet

router = DefaultRouter()

router.register("tickets",TicketViewSet,basename="Ticket")

urlpatterns = router.urls

# /api/tickets/?status=OPEN

# /api/tickets/?priority=HIGH

# /api/tickets/?assigned_to=3

# urlpatterns = [
#     # path("test/",test_api,),
#     # path("",get_tickets,),
#     # path("<int:pk>/",get_ticket),
#     # path("update/<int:pk>/",update_ticket),
#     # path("delete/<int:pk>/",delete_ticket),
#     # path("create/",create_ticket),
#     # path("api/",TicketApiView.as_view()),
#     # path("api/<int:pk>",TicketApiView.as_view()),
#     # path("mixi/",TicketListAPIVIEW.as_view()),
#     router.urls
# ]




