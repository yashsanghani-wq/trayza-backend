from rest_framework.response import Response
from rest_framework import status, generics
from trayza.Utils.permissions import *
from .serializers import *

# --------------------    EventBookingViewSet    --------------------


class EventBookingViewSet(generics.GenericAPIView):
    serializer_class = EventBookingSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def post(self, request):
        sessions = request.data.get("sessions", [])
        
        # Process each session's selected_items and extra_service
        for session in sessions:
            # Convert the selected_items payload for the session
            selected_items = session.get("selected_items", {})
            converted_payload = {
                key: [{"name": item} for item in value]
                for key, value in selected_items.items()
            }
            session["selected_items"] = converted_payload
            
            # Calculate extra_service_amount for the session
            amount = 0
            extra_services = session.get("extra_service", [])
            for extra_service in extra_services:
                if extra_service.get("amount"):
                    amount = amount + int(extra_service.get("amount"))
            session["extra_service_amount"] = str(amount)

        request.data["sessions"] = sessions

        serializer = EventBookingSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "EventBooking created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": False,
                "message": "Something went wrong",
                "data": {},
            },
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        queryset = (
            EventBooking.objects.prefetch_related('sessions')
            .filter(status__in=["confirm", "completed"])
            .order_by("-date")
        )
        for event_booking in queryset:
            changed = False
            for session in event_booking.sessions.all():
                if session.extra_service_amount == "0" and all(service.get("extra") for service in session.extra_service):
                    session.extra_service_amount = str(sum(int(service.get("amount", 0)) for service in session.extra_service))
                    session.save()
                    changed = True
                
        serializer = EventBookingSerializer(queryset, many=True)
        return Response(
            {
                "status": True,
                "message": "EventBooking list",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class EventBookingGetViewSet(generics.GenericAPIView):
    serializer_class = EventBookingSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def put(self, request, pk=None):
        try:
            eventbooking = EventBooking.objects.get(pk=pk)
            sessions = request.data.get("sessions")
            
            if sessions is not None:
                # Process each session
                for session in sessions:
                    selected_items = session.get("selected_items", {})
                    extra_service = session.get("extra_service", [])
                    
                    if all(service.get("extra") for service in extra_service):
                        session["extra_service_amount"] = str(sum(int(service.get("amount", 0)) for service in extra_service))
                    
                    if selected_items and isinstance(selected_items, dict):
                        # Some logic might pass already converted items, check if it's list of strings
                        is_unconverted = any(isinstance(v, list) and len(v) > 0 and isinstance(v[0], str) for v in selected_items.values())
                        
                        if is_unconverted:
                            converted_payload = {
                                key: [{"name": item} for item in value]
                                for key, value in selected_items.items()
                            }
                            session["selected_items"] = converted_payload
                
                request.data["sessions"] = sessions

            # Partially update the instance with only provided fields
            serializer = EventBookingSerializer(eventbooking, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "EventBooking updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        except EventBooking.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "EventBooking not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def get(self, request, pk=None):
        try:
            eventbooking = EventBooking.objects.get(pk=pk)
            serializer = EventBookingSerializer(eventbooking)
            return Response(
                {
                    "status": True,
                    "message": "EventBooking retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except EventBooking.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "EventBooking not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, pk=None):
        try:
            eventbooking = EventBooking.objects.get(pk=pk)
            eventbooking.delete()
            return Response(
                {
                    "status": True,
                    "message": "EventBooking deleted successfully",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        except EventBooking.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "EventBooking not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )


# --------------------    StatusChangeEventBookingViewSet    --------------------


class StatusChangeEventBookingViewSet(generics.GenericAPIView):
    serializer_class = EventBookingSerializer
    permission_classes = [IsOwnerOrAdmin]

    def post(self, request, pk=None):
        try:
            queryset = EventBooking.objects.get(pk=pk)
            # The status change logic is mostly for the main booking status
            queryset.status = request.data.get("status")
            queryset.save()
            return Response(
                {
                    "status": True,
                    "message": "EventBooking status changed",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        except EventBooking.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "EventBooking not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )


# --------------------    PendingEventBookingViewSet    --------------------


class PendingEventBookingViewSet(generics.GenericAPIView):
    serializer_class = EventBookingSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get(self, request):
        queryset = EventBooking.objects.prefetch_related('sessions').filter(status="pending").order_by("-date")
        serializer = EventBookingSerializer(queryset, many=True)
        return Response(
            {
                "status": True,
                "message": "EventBooking list",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class GetAllEvent(generics.GenericAPIView):
    def get(self,request):
        queryset = EventBooking.objects.prefetch_related('sessions').all().order_by("-date")
        serializer = EventBookingSerializer(queryset, many=True)
        return Response(
            {
                "status": True,
                "message": "EventBooking list",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )