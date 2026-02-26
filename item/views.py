from collections import defaultdict

from rest_framework.response import Response
from rest_framework import status, generics
from ListOfIngridients.models import EventIngridientList, IngridientsCategory
from ListOfIngridients.serializers import IngridientsCategorySerializer, EventIngridientListSerializer
from trayza.Utils.permissions import *
from eventbooking.models import EventBooking
from stockmanagement.models import StokeItem
from .models import Item
from .serializers import *
from trayza.Utils.scale_factor import *


# --------------------    ItemViewSet    --------------------


class ItemViewSet(generics.GenericAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def post(self, request):
        if Item.objects.filter(name=request.data.get("name")).exists():
            return Response(
                {
                    "status": False,
                    "message": "Item already exists",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Item created successfully",
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
        # Get all item IDs that are already used in RecipeIngredient
        used_item_ids = set(RecipeIngredient.objects.values_list("item__pk", flat=True))

        # Exclude those items from the queryset
        available_items = Item.objects.exclude(id__in=used_item_ids)

        # Serialize the queryset
        serializer = ItemSerializer(available_items, many=True)

        return Response(
            {
                "status": True,
                "message": "Item list",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ItemGetViewSet(generics.GenericAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def put(self, request, pk=None):
        try:
            item = Item.objects.get(pk=pk)
            serializer = ItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Item updated successfully",
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
        except Item.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Item not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def get(self, request, pk=None):
        try:
            item = Item.objects.get(pk=pk)
            serializer = ItemSerializer(item)
            return Response(
                {
                    "status": True,
                    "message": "Item retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Item.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Item not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, pk=None):
        try:
            item = Item.objects.get(pk=pk)
            item.delete()
            return Response(
                {
                    "status": True,
                    "message": "Item deleted successfully",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        except Item.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Item not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )


# --------------------    RecipeIngredientViewSet    --------------------


class RecipeIngredientViewSet(generics.GenericAPIView):
    serializer_class = RecipeIngredientSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def post(self, request):
        serializer = RecipeIngredientSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Recipe Ingredient created successfully",
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
        recipe_ingredient = RecipeIngredient.objects.all()
        serializer = RecipeIngredientSerializer(recipe_ingredient, many=True)
        for data in serializer.data:
            item = Item.objects.filter(pk=data.get("item")).values("name").first()
            data["item"] = item
        return Response(
            {
                "status": True,
                "message": "Recipe Ingredient List",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class EditRecipeIngredientViewSet(generics.GenericAPIView):
    serializer_class = EditRecipeIngredientSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def put(self, request, pk=None):
        try:
            item = RecipeIngredient.objects.get(pk=pk)
            serializer = EditRecipeIngredientSerializer(
                item, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Recipe Ingredient updated successfully",
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
        except Item.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Recipe Ingredient not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def get(self, request, pk=None):
        try:
            item = RecipeIngredient.objects.get(pk=pk)
            serializer = RecipeIngredientSerializer(item)
            return Response(
                {
                    "status": True,
                    "message": "Recipe Ingredient retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Item.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Recipe Ingredient not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, pk=None):
        try:
            item = RecipeIngredient.objects.get(pk=pk)
            item.delete()
            return Response(
                {
                    "status": True,
                    "message": "Recipe Ingredient deleted successfully",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        except Item.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Recipe Ingredient not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )


# --------------------    Ingredient Calculator API    --------------------

# class IngredientCalculatorView(generics.GenericAPIView):
#     """Compute ingredient quantities for a list of dishes given a person count."""
#     serializer_class = IngredientCalcSerializer
#     permission_classes = [IsAdminUserOrReadOnly]

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         if not serializer.is_valid():
#             return Response({
#                 "status": False,
#                 "message": "Validation error",
#                 "errors": serializer.errors,
#             }, status=status.HTTP_400_BAD_REQUEST)

#         items = serializer.validated_data["items"]
#         persons = serializer.validated_data["persons"]

#         recipes = RecipeIngredient.objects.select_related("item").filter(
#             item__name__in=items
#         )

#         # accumulate ingredient totals
#         totals = {}
#         import re

#         for ri in recipes:
#             ingredients = ri.ingredients
#             recipe_person_count = ri.person_count if ri.person_count > 0 else 1
#             scale_factor = persons / recipe_person_count

#             if isinstance(ingredients, dict):
#                 for ing, qty in ingredients.items():
#                     try:
#                         match = re.search(r"^\s*([\d\.]+)", str(qty))
#                         if match:
#                             num = float(match.group(1))
#                             scaled_num = num * scale_factor
#                             formatted = f"{scaled_num:.2f}".rstrip('0').rstrip('.')
#                             final_qty = str(qty).replace(match.group(1), formatted, 1)
#                         else:
#                             final_qty = str(qty)
#                     except Exception:
#                         final_qty = str(qty)

#                     totals.setdefault(ing, []).append({
#                         "item": ri.item.name,
#                         "quantity": final_qty,
#                     })
#             else:
#                 # list of ingredient names without quantities
#                 for ing in ingredients:
#                     totals.setdefault(ing, []).append({
#                         "item": ri.item.name,
#                         "quantity": "",
#                     })

#         return Response({
#             "status": True,
#             "message": "Calculated ingredients",
#             "data": totals,
#         }, status=status.HTTP_200_OK)


class IngredientCalculatorView(generics.GenericAPIView):

    def post(self, request):
        serializer = IngredientCalcSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_names = serializer.validated_data["items"]
        persons = serializer.validated_data["persons"]

        total_ingredients = defaultdict(float)
        units = {}

        items = Item.objects.filter(name__in=item_names).select_related("recipe")

        if not items.exists():
            return Response(
                {"error": "No valid items found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in items:

            if not hasattr(item, "recipe"):
                continue

            recipe = item.recipe
            scale_factor = persons / recipe.person_count

            for ingredient, qty in recipe.ingredients.items():

                ingredient_name = ingredient.strip().lower()

                value, unit = parse_quantity(qty)

                total_ingredients[ingredient_name] += value * scale_factor
                units[ingredient_name] = unit

        result = {}

        # attach category information for each ingredient, using ListOfIngridients models
        ingredient_names = [name for name in total_ingredients.keys()]
        from ListOfIngridients.models import IngridientsItem
        items_with_categories = (
            IngridientsItem.objects.filter(name__in=ingredient_names)
            .select_related("category")
        )
        category_map = {item.name.strip().lower(): item.category.name for item in items_with_categories}

        for name, value in total_ingredients.items():
            converted_value, converted_unit = convert_unit(value, units[name])
            cat = category_map.get(name.strip().lower(), "")
            result[name] = {
                "quantity": f"{converted_value} {converted_unit}",
                "category": cat,
            }

        return Response({
            "persons": persons,
            "ingredients_required": result
        }, status=status.HTTP_200_OK)

# --------------------    CommonIngredientsViewSet    --------------------


class CommonIngredientsViewSet(generics.GenericAPIView):
    serializer_class = EventIngridientListSerializer

    def get_recipe_for_item(self, item_name):
        try:
            return (
                RecipeIngredient.objects.select_related("item")
                .get(item__name=item_name)
                .ingredients
            )
        except RecipeIngredient.DoesNotExist:
            return None

    def consolidate_categories(self, data):
        consolidated = {}
        for category in data:
            name = category["name"]
            if name not in consolidated:
                consolidated[name] = {"name": name, "data": []}
            item_dict = {item["item"]: item for item in consolidated[name]["data"]}
            for item in category["data"]:
                item_name = item["item"]
                if item_name in item_dict:
                    existing = item_dict[item_name]
                    existing_use_items = {
                        frozenset((k, v) for k, v in ui.items()) 
                        for ui in existing["use_item"]
                    }
                    for ui in item["use_item"]:
                        ui_set = frozenset((k, v) for k, v in ui.items())
                        if ui_set not in existing_use_items:
                            existing["use_item"].append(ui)
                else:
                    item_dict[item_name] = item
                    consolidated[name]["data"].append(item)
        return list(consolidated.values())

    def post(self, request):
        event_id = request.data.get("event_id")
        if not event_id:
            return Response(
                {"status": False, "message": "Event ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        try:
            # 1. Fetch Event
            try:
                event = EventBooking.objects.prefetch_related('sessions').get(id=event_id)
            except EventBooking.DoesNotExist:
                return Response(
                    {"status": False, "message": "Event not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 2. Check if list already exists
            existing_instance = None
            existing_list_data = []
            
            try:
                existing_instance = EventIngridientList.objects.get(event_id=event_id)
                existing_list_data = existing_instance.ingridient_list_data
            except EventIngridientList.DoesNotExist:
                pass

            # 3. Collect selected dishes from all sessions
            selected_dishes = []
            for session in event.sessions.all():
                try:
                    estimated_persons = int(session.estimated_persons)
                except (ValueError, TypeError):
                    estimated_persons = 100
                    
                for category, category_items in session.selected_items.items():
                    for item in category_items:
                        selected_dishes.append({
                            "item": item["name"], 
                            "item_category": category,
                            "session_time": session.event_time,
                            "estimated_persons": estimated_persons
                        })
            
            # 4. Fetch recipes
            item_names = [dish["item"] for dish in selected_dishes]
            recipes = {
                ri.item.name: ri
                for ri in RecipeIngredient.objects.select_related("item").filter(
                    item__name__in=item_names
                )
            }

            # 5. Map ingredients to dishes
            import re
            ingredient_to_dishes = defaultdict(list)
            for dish in selected_dishes:
                recipe = recipes.get(dish["item"])
                if not recipe:
                    continue
                
                ingredients = recipe.ingredients
                recipe_person_count = recipe.person_count if recipe.person_count > 0 else 100
                scale_factor = dish["estimated_persons"] / recipe_person_count

                if isinstance(ingredients, list):
                    for ingredient in ingredients:
                        ingredient_to_dishes[ingredient].append({
                            "item_name": dish["item"],
                            "item_category": dish["item_category"],
                            "quantity": "",
                        })
                elif isinstance(ingredients, dict):
                    for ingredient, quantity_str in ingredients.items():
                        try:
                            # Try to extract the numeric part from beginning of string
                            match = re.search(r"^\s*([\d\.]+)", str(quantity_str))
                            if match:
                                num = float(match.group(1))
                                scaled_num = num * scale_factor
                                formatted_num = f"{scaled_num:.2f}".rstrip('0').rstrip('.')
                                final_quantity = str(quantity_str).replace(match.group(1), formatted_num, 1)
                            else:
                                final_quantity = str(quantity_str)
                        except Exception:
                            final_quantity = str(quantity_str)

                        ingredient_to_dishes[ingredient].append({
                            "item_name": dish["item"],
                            "item_category": dish["item_category"],
                            "quantity": final_quantity,
                        })

            # 6. Fetch categories and stock
            ingredient_categories = {
                item["name"]: data["name"]
                for data in IngridientsCategorySerializer(
                    IngridientsCategory.objects.all(), many=True
                ).data
                for item in data.get("items", [])
            }
            
            ingredient_names = set(ingredient_to_dishes.keys())
            stock_items = {
                si.name: {"quantity": str(si.quantity), "type": si.type}
                for si in StokeItem.objects.filter(name__in=ingredient_names)
            }

            # 7. Prepare grouped data
            response_data = defaultdict(list)
            common_category = "કોમન"

            for ingredient, dishes in ingredient_to_dishes.items():
                stock_info = stock_items.get(ingredient, {"quantity": "", "type": ""})
                category = ingredient_categories.get(ingredient)
                
                cat_to_use = category if category else common_category
                
                # Prevent duplicates
                if not any(entry["item"] == ingredient for entry in response_data[cat_to_use]):
                    response_data[cat_to_use].append({
                        "item": ingredient,
                        "quantity_type": "",
                        "godown_quantity": stock_info["quantity"],
                        "godown_quantity_type": stock_info["type"],
                        "use_item": dishes if category else [{
                            "item_name": ingredient,
                            "item_category": common_category,
                            "quantity": "",
                        }],
                        "total_quantity": "0",
                    })

            formatted_response = [
                {"name": category, "data": items}
                for category, items in response_data.items()
            ]
            
            # 8. Merge data if existing
            if existing_instance:
                consolidated_list = self.consolidate_categories(existing_list_data + formatted_response)
            else:
                consolidated_list = formatted_response
                
            # 9. DRF Serializer logic for Create / Update
            payload = {
                "event_id": event_id,
                "ingridient_list_data": consolidated_list
            }

            if existing_instance:
                serializer = self.serializer_class(existing_instance, data=payload, partial=True)
                success_status = status.HTTP_200_OK
                message = "Ingredients list updated successfully"
            else:
                serializer = self.serializer_class(data=payload)
                success_status = status.HTTP_201_CREATED
                message = "Ingredients list created successfully"

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": message,
                        "data": serializer.data,
                    },
                    status=success_status,
                )
            else:
                return Response(
                    {
                        "status": False,
                        "message": "Validation Error",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
