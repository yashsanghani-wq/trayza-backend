from rest_framework.response import Response
from rest_framework import status, generics
from trayza.Utils.permissions import *
from .serializers import *
from collections import defaultdict
from trayza.Utils.scale_factor import *
from item.models import RecipeIngredient

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
            EventBooking.objects.prefetch_related(
                "sessions__staff_assignments__staff__role",
                "sessions__staff_assignments__role_at_event",
            )
            .filter(status__in=["confirm", "completed"])
            .order_by("-date")
        )
        for event_booking in queryset:
            changed = False
            for session in event_booking.sessions.all():
                if session.extra_service_amount == "0" and all(
                    service.get("extra") for service in session.extra_service
                ):
                    session.extra_service_amount = str(
                        sum(
                            int(service.get("amount", 0))
                            for service in session.extra_service
                        )
                    )
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
                        session["extra_service_amount"] = str(
                            sum(
                                int(service.get("amount", 0))
                                for service in extra_service
                            )
                        )

                    if selected_items and isinstance(selected_items, dict):
                        # Some logic might pass already converted items, check if it's list of strings
                        is_unconverted = any(
                            isinstance(v, list) and len(v) > 0 and isinstance(v[0], str)
                            for v in selected_items.values()
                        )

                        if is_unconverted:
                            converted_payload = {
                                key: [{"name": item} for item in value]
                                for key, value in selected_items.items()
                            }
                            session["selected_items"] = converted_payload

                request.data["sessions"] = sessions

            # Partially update the instance with only provided fields
            serializer = EventBookingSerializer(
                eventbooking, data=request.data, partial=True
            )
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
            eventbooking = EventBooking.objects.prefetch_related(
                "sessions__staff_assignments__staff__role",
                "sessions__staff_assignments__role_at_event",
            ).get(pk=pk)
            serializer = EventBookingSerializer(eventbooking)

            response_data = serializer.data

            # 🔥 Loop over serialized sessions
            for session_dict, session_obj in zip(
                response_data["sessions"], eventbooking.sessions.all()
            ):

                try:
                    persons = int(session_obj.estimated_persons)
                except:
                    persons = 100

                dishes_data = session_obj.selected_items.get("Dishes", [])
                total_ingredients = defaultdict(
                    lambda: {"value": 0, "unit": "", "used_in": set()}
                )

                # Collect dish names
                dish_names = [dish.get("name").strip() for dish in dishes_data]

                # Fetch recipes in one query
                recipes = {
                    ri.item.name.strip(): ri
                    for ri in RecipeIngredient.objects.select_related("item").filter(
                        item__name__in=dish_names
                    )
                }

                # Calculate ingredients for this session
                for dish_name in dish_names:

                    recipe = recipes.get(dish_name)
                    if not recipe:
                        continue

                    recipe_person_count = (
                        recipe.person_count if recipe.person_count > 0 else 100
                    )
                    scale_factor = persons / recipe_person_count

                    if isinstance(recipe.ingredients, dict):
                        for ingredient, qty_str in recipe.ingredients.items():

                            ingredient_name = ingredient.strip()

                            value, unit = parse_quantity(qty_str)
                            scaled_value = value * scale_factor

                            total_ingredients[ingredient_name]["value"] += scaled_value
                            total_ingredients[ingredient_name]["unit"] = unit
                            total_ingredients[ingredient_name]["used_in"].add(dish_name)

                # Convert units
                final_ingredients = {}

                # lookup categories for ingredients from the ListOfIngridients app
                ingredient_names = [name for name in total_ingredients.keys()]
                from ListOfIngridients.models import IngridientsItem

                items_with_categories = IngridientsItem.objects.filter(
                    name__in=ingredient_names
                ).select_related("category")
                category_map = {
                    item.name.strip().lower(): item.category.name
                    for item in items_with_categories
                }

                from stockmanagement.models import StokeItem

                # Build stock_map for recipe-calculated ingredients
                stock_items = StokeItem.objects.filter(name__in=ingredient_names)
                stock_map = {
                    item.name.strip().lower(): {
                        "quantity": str(item.quantity),
                        "type": item.type,
                    }
                    for item in stock_items
                }

                for ingredient, data in total_ingredients.items():
                    converted_value, converted_unit = convert_unit(
                        data["value"], data["unit"]
                    )
                    cat = category_map.get(ingredient.strip().lower(), "")
                    stock_info = stock_map.get(ingredient.strip().lower(), {})
                    vendor_info = session_obj.assigned_vendors.get(ingredient, None)

                    # store quantity, category, available stock quantity and its type
                    final_ingredients[ingredient] = {
                        "quantity": f"{converted_value} {converted_unit}",
                        "category": cat,
                        "available_stock": stock_info.get("quantity", "0"),
                        "stock_type": stock_info.get("type", ""),
                        "used_in": list(data["used_in"]),
                    }
                    if vendor_info:
                        final_ingredients[ingredient]["vendor"] = vendor_info

                # ✅ Always include all categories marked as `is_common=True`
                common_items = IngridientsItem.objects.filter(
                    category__is_common=True
                ).select_related("category")

                common_names = [item.name for item in common_items]
                common_stock_items = StokeItem.objects.filter(name__in=common_names)
                common_stock_map = {
                    item.name.strip().lower(): {
                        "quantity": str(item.quantity),
                        "type": item.type,
                    }
                    for item in common_stock_items
                }

                for item in common_items:
                    key = item.name.strip().lower()
                    # Only add if not already calculated from recipe
                    if item.name not in final_ingredients:
                        stock_info = common_stock_map.get(key, {})
                        vendor_info = session_obj.assigned_vendors.get(item.name, None)

                        final_ingredients[item.name] = {
                            "quantity": "0",
                            "category": item.category.name,
                            "available_stock": stock_info.get("quantity", "0"),
                            "stock_type": stock_info.get("type", ""),
                            "used_in": [],
                        }
                        if vendor_info:
                            final_ingredients[item.name]["vendor"] = vendor_info

                # 🔥 Inject inside session dictionary
                session_dict["ingredients_required"] = final_ingredients

            return Response(
                {
                    "status": True,
                    "message": "EventBooking retrieved successfully",
                    "data": response_data,
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
                status=status.HTTP_404_NOT_FOUND,
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
        queryset = (
            EventBooking.objects.prefetch_related(
                "sessions__staff_assignments__staff__role",
                "sessions__staff_assignments__role_at_event",
            )
            .filter(status="pending")
            .order_by("-date")
        )
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
    def get(self, request):
        queryset = (
            EventBooking.objects.prefetch_related(
                "sessions__staff_assignments__staff__role",
                "sessions__staff_assignments__role_at_event",
            )
            .all()
            .order_by("-date")
        )
        serializer = EventBookingSerializer(queryset, many=True)
        return Response(
            {
                "status": True,
                "message": "EventBooking list",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
