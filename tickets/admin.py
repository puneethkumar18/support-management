from django.contrib import admin
from tickets.models import Ticket,TicketHistory,TicketAttachment

# Register your models here.
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title"
    )

@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "event_type",
        "changed_by"
    )

@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "ticket",
        "uploaded_by",
        "file"
    )