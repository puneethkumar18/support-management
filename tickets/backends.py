from rest_framework.filters import BaseFilterBackend

class TicketFilterBackend(BaseFilterBackend):

    def filter_queryset(self,request,queryset,view):
        status = request.query_params.get("status")
        priority = request.query_params.get("priority")
        assigned_to = request.query_params.get("assigned_to")

        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if assigned_to:
            assigned_to = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset