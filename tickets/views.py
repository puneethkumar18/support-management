from django.shortcuts import render,redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes,action
from tickets.models import Ticket,TicketHistory,TicketAttachment
from tickets.serializers import TicketSerializer,TicketHistorySerializer,TicketAttachmentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.contrib.auth.models import User
from comments.serializers import CommentSerializer
from tickets.backends import TicketFilterBackend
from rest_framework import filters
from django.core.cache import cache


# Create your views here.
@api_view(['GET'])
def test_api(request):
    return Response({"message":"API is Working!"})


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    queryset = Ticket.objects.all()

    # FILTERS
    filter_backends = [TicketFilterBackend,filters.OrderingFilter]

    # ORDERING

    ordering_fields = ['created_at', 'priority', 'status']


    # my-created
    @action(detail=False,methods=["get"])
    def my_created(self,request,pk=None):
        tickets = Ticket.objects.filter(created_by=request.user)
        serializer =  TicketSerializer(tickets,many=True)
        return Response(serializer.data,status=200)
    

    # my-assigned
    @action(detail=False,methods=["get"])
    def my_assigned(self,request,pk=None):
        tickets = Ticket.objects.filter(assigned_to=request.user)
        serializer = TicketSerializer(tickets,many=True)
        return Response(serializer.data,status=200)


    # TICKET ATTACHMENT UPLOAD
    @action(detail=True,methods=["post"])
    def upload_attachment(self,request,pk=None):
        ticket = self.get_object()
        file = request.FILES.get("file")

        if not file:
            return Response({"error":"No File Uploaded"},status=400)
        

        file
        
        attachment = TicketAttachment.objects.create(
            uploaded_by = request.user,
            file = file,
            ticket = ticket
        )

        serializer = TicketAttachmentSerializer(attachment)

        return Response(serializer.data,status=201)


    # TICKET ATTACHMENT LIST
    @action(detail=True,methods=["get"])
    def attachments(self,request,pk=None):
        ticket = self.get_object()
        attachments = ticket.TicketAttachments.all()
        serializer = TicketAttachmentSerializer(attachments,many= True)
        return Response(serializer.data,status=200)

    # DASHBOARD
    @action(detail=False,methods=["get"])
    def dashboard(self,request,pk=None):
        cache_key = f"dashboard_{request.user.id}"
        data = cache.get(cache_key)
        if data:
            print("CACHE HIT")
            return Response(data=data)
        print("CACHE MISS")
        user = request.user
        if user.role == "SUPERVISOR":
            tickets = Ticket.objects.all()
        elif user.role == "REQUESTER":
            tickets = Ticket.objects.filter(created_by=user)
        else:
            tickets = Ticket.objects.filter(assigned_to=user)
        data = {
            "Total":tickets.count(),
            "open_tickets":tickets.filter(status="OPEN").count(),
            "in_progess_tickets":tickets.filter(status="IN_PROGRESS").count(),
            "resolved_tickets":tickets.filter(status="RESOLVED").count(),
            "closed_tickets":tickets.filter(status="CLOSED").count()
        }
        cache.set(cache_key,data,timeout=60)
        return Response(data,status=200)

    # TICKET HISTORY
    @action(detail=True,methods=["get","post"])
    def history(self,request,pk=None):
        ticket = self.get_object()
        if request.method == "GET":
            history = ticket.TicketHistory.all()
            serializer = TicketHistorySerializer(history,many=True)
            return Response(serializer.data,status=200)
        
        serializer = TicketHistorySerializer(request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save(changed_by=request.user,ticket = ticket)
        return Response(serializer.data,status=200)


    # COMMENTS
    @action(detail=True,methods=["get","post"])
    def comments(self, request, pk=None):
        ticket = self.get_object()
        if request.method == "GET":
            serializer = CommentSerializer(
                ticket.comments.all(),
                many=True
            )
            return Response(serializer.data)
        allowed_users = [ticket.created_by,ticket.assigned_to]
        serializer = CommentSerializer(data=request.data,many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket,user = request.user)
        return Response(serializer.data, status=201)

    # TICKETS
    def get_queryset(self):
        user = self.request.user
        status_param = self.request.query_params.get("status")
        query = Ticket.objects.all()
        if status_param:
            query = query.filter(status=status_param)
        if user.role == "SUPERVISOR":
            return  query
        elif user.role == "REQUESTER":
            query = query.filter(created_by=user)
        else:
            query = query.filter(assigned_to=user)

        if status_param:
            query = query.filter(status=status_param)
        return query

    def perform_create(self,serializer):
        serializer.save(created_by = self.request.user)

    def perform_update(self, serializer):
        user = self.request.user
        request = self.request
        if 'assigned_to' in request.data:
            if not request.user.role ==  "SUPERVISOR":
                raise PermissionError(
                    "Only SUPERVISOR can assign tickets..."
                )
            
        if user.is_supervisor:
            if request.data.get("status")  and request.data.get("status") in ["IN_PROGESS","RESOLVED"]:
                raise PermissionError(
                    "SUPERVISOR Can only close the Ticket"
                )
        elif user.is_requester:
            if serializer.instance.assigned_to:
                raise PermissionError(
                    "Cannot modify assigned tickets..."
                )
            if "status"  in request.data:
                raise PermissionError(
                    "REQUESTER Can't change the Status."
                )

        else:
            allowed_fields = {"status"}
            incoming_fields = set(self.request.data.keys())
            if not incoming_fields.issubset(allowed_fields):
                raise PermissionError(
                    "AI Agent can only update status."
                )
            if request.data['status'] == "CLOSED":
                raise PermissionError(
                    "AI Agent can't Close the Tickets",
                )


        serializer.save()






    

# class TicketListAPIVIEW(mixins.ListModelMixin,mixins.CreateModelMixin,generics.GenericAPIView):
#     queryset = Ticket.objects.all()
#     serializer_class = TicketSerializer


#     # def perform_create(self,serializer):
#     #     serializer.save(created_by = self.request.user)

#     def create(self,request,*args,**kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(created_by = request.user)
#         return Response(serializer.data,status=status.HTTP_201_CREATED)

#     def get(self,request,*args,**kwargs):
#         return self.list(request,*args,**kwargs)

#     def post(self,request,*args,**kwargs):
#         return self.create(request,*args,**kwargs)


# class TicketApiView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self,request,*args,**kwargs):
#         tickets = Ticket.objects.all()
#         serializer = TicketSerializer(tickets, many= True)
#         return Response(serializer.data)

#     def put(self,request,pk):
#         try:
#             ticket = Ticket.objects.get(pk = pk)
#         except Ticket.DoesNotExist:
#             return Response({"error": "Ticket not found"},status=status.HTTP_404_NOT_FOUND)
        
#         serializer = TicketSerializer(ticket,data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(
#             serializer.errors,
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     def delete(self,request,pk):
#         try:
#             ticket = Ticket.objects.get(pk=pk)
#         except Ticket.DoesNotExist:
#             return Response(
#                 {"error": "Ticket not found"},
#                 status=status.HTTP_404_NOT_FOUND
#                 )
#         ticket.delete()
#         return Response(
#             {"message": "Ticket deleted successfully"},
#             status=status.HTTP_200_OK
#         )







# @api_view(['GET'])
# def get_tickets(request):
#     tickets = Ticket.objects.all()
#     serializer = TicketSerializer(tickets, many = True)
#     return  Response(serializer.data)


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def create_ticket(request):
#     serializer = TicketSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save(created_by=request.user)
#         return Response(serializer.data,status=status.HTTP_201_CREATED)

#     return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


# @api_view(["GET"])
# def get_ticket(request,pk):
#     try:
#         ticket = Ticket.objects.get(pk=pk)
#     except:
#         return Response({"error":f"Ticket with {pk} Doesnot Exist!"},status=status.HTTP_404_NOT_FOUND)
#     serializer = TicketSerializer(ticket)
#     return Response(serializer.data,status=status.HTTP_200_OK)

# @api_view(["PUT"])
# def update_ticket(request,pk):
#     try:
#         ticket = Ticket.objects.get(pk=pk)
#     except Ticket.DoesNotExist:
#         return Response(
#             {"error": "Ticket not found"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     serializer = TicketSerializer(
#         ticket,
#         data=request.data
#     )
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(
#         serializer.errors,
#         status=status.HTTP_400_BAD_REQUEST
#     )


# @api_view(["DELETE"])
# def delete_ticket(request,pk):
#     try:
#         ticket = Ticket.objects.get(pk=pk)
#     except Ticket.DoesNotExist:
#         return Response(
#             {"error": "Ticket not found"},
#             status=status.HTTP_404_NOT_FOUND
#         )
#     ticket.delete()
#     return Response(
#         {"message": "Ticket deleted successfully"},
#         status=status.HTTP_200_OK
#     )


    