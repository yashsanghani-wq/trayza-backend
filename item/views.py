from collections import defaultdict
import json
from rest_framework.response import Response
from rest_framework import status, generics
from ListOfIngridients.models import EventIngridientList, IngridientsCategory
from ListOfIngridients.serializers import IngridientsCategorySerializer
from trayza.Utils.permissions import *
from eventbooking.models import EventBooking
from stockmanagement.models import StokeItem
from .models import Item
from .serializers import *


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


# --------------------    CommonIngredientsViewSet    --------------------


class CommonIngredientsViewSet(generics.GenericAPIView):
    # permission_classes = [IsAdminUserOrReadOnly]

    def get_recipe_for_item(self, item_name):
        """
        Efficiently retrieve recipe ingredients for a given item.

        Args:
            item_name (str): Name of the item to find recipe for.

        Returns:
            dict/list/None: Ingredients for the item or None if not found.
        """
        try:
            return (
                RecipeIngredient.objects.select_related("item")
                .get(item__name=item_name)
                .ingredients
            )
        except RecipeIngredient.DoesNotExist:
            return None

    def consolidate_categories(self, data):
        """
        Consolidate and deduplicate categories and their items.
        
        Args:
            data (list): List of category dictionaries with their data.
            
        Returns:
            list: Consolidated list with unique items per category.
        """
        # Create a dictionary to store merged categories
        consolidated = {}

        # Process each category
        for category in data:
            name = category["name"]
            
            # Initialize if category doesn't exist
            if name not in consolidated:
                consolidated[name] = {"name": name, "data": []}
                
            # Use a temporary dictionary to track items by name
            item_dict = {item["item"]: item for item in consolidated[name]["data"]}
            
            # Process each item in the current category
            for item in category["data"]:
                item_name = item["item"]
                
                if item_name in item_dict:
                    # Merge use_item lists efficiently
                    existing = item_dict[item_name]
                    existing_use_items = {
                        frozenset((k, v) for k, v in ui.items()) 
                        for ui in existing["use_item"]
                    }
                    
                    # Add new use_items that don't exist yet
                    for ui in item["use_item"]:
                        ui_set = frozenset((k, v) for k, v in ui.items())
                        if ui_set not in existing_use_items:
                            existing["use_item"].append(ui)
                else:
                    # Add new item to the dictionary
                    item_dict[item_name] = item
                    consolidated[name]["data"].append(item)

        # Convert back to list format
        return list(consolidated.values())

    def post(self, request):
        """
        Process event ingredients analysis.

        Args:
            request: HTTP request object.

        Returns:
            Response: JSON response with ingredient analysis.
        """
        # Validate event ID
        event_id = request.data.get("event_id")
        if not event_id:
            return Response(
                {"status": False, "message": "Event ID is required"},
                status=status.HTTP_200_OK,
            )
            
        try:
            # Fetch event
            try:
                event = EventBooking.objects.get(id=event_id)
            except EventBooking.DoesNotExist:
                return Response(
                    {"status": False, "message": "Event not found"},
                    status=status.HTTP_200_OK,
                )

            # Check if event ingredient list already exists
            event_ingredient_list = None
            existing_list_data = []
            is_existing = False
            
            try:
                event_ingredient_list = EventIngridientList.objects.get(event_id=event_id)
                existing_list_data = event_ingredient_list.ingridient_list_data
                is_existing = True
            except EventIngridientList.DoesNotExist:
                pass

            # Collect selected dishes directly from the JSONField
            selected_dishes = [
                {"item": item["name"], "item_category": category}
                for category, category_items in event.selected_items.items()
                for item in category_items
            ]
            
            # Optimize recipe ingredient retrieval
            item_names = [dish["item"] for dish in selected_dishes]
            recipe_ingredients = {
                ri.item.name: ri.ingredients
                for ri in RecipeIngredient.objects.select_related("item").filter(
                    item__name__in=item_names
                )
            }

            # Prepare ingredient-to-dishes mapping
            ingredient_to_dishes = defaultdict(list)
            for dish in selected_dishes:
                ingredients = recipe_ingredients.get(dish["item"])
                if not ingredients:
                    continue
                    
                if isinstance(ingredients, list):
                    for ingredient in ingredients:
                        ingredient_to_dishes[ingredient].append({
                            "item_name": dish["item"],
                            "item_category": dish["item_category"],
                            "quantity": "",
                        })
                elif isinstance(ingredients, dict):
                    for ingredient, quantity in ingredients.items():
                        ingredient_to_dishes[ingredient].append({
                            "item_name": dish["item"],
                            "item_category": dish["item_category"],
                            "quantity": quantity,
                        })

            # Bulk fetch ingredient categories
            ingredient_categories = {
                item["name"]: data["name"]
                for data in IngridientsCategorySerializer(
                    IngridientsCategory.objects.all(), many=True
                ).data
                for item in data.get("items", [])
            }
            
            # Prefetch stock items in bulk
            ingredient_names = set(ingredient_to_dishes.keys())
            stock_items = {
                si.name: {"quantity": str(si.quantity), "type": si.type}
                for si in StokeItem.objects.filter(name__in=ingredient_names)
            }

            # Prepare response data with efficient category mapping
            response_data = defaultdict(list)
            common_category = "કોમન"  # Store the common category name

            for ingredient, dishes in ingredient_to_dishes.items():
                # Get stock information
                stock_info = stock_items.get(ingredient, {"quantity": "", "type": ""})
                
                # Find the category for this ingredient
                category = ingredient_categories.get(ingredient)
                
                if category:
                    # Only add if this ingredient isn't already in this category
                    if not any(entry["item"] == ingredient for entry in response_data[category]):
                        response_data[category].append({
                            "item": ingredient,
                            "quantity_type": "",
                            "godown_quantity": stock_info["quantity"],
                            "godown_quantity_type": stock_info["type"],
                            "use_item": dishes,
                            "total_quantity": "0",
                        })
                else:
                    # Handle items without a category using the common category
                    for key, val in ingredient_categories.items():
                        if val == common_category:
                            if not any(entry["item"] == key for entry in response_data[val]):
                                response_data[val].append({
                                    "item": key,
                                    "quantity_type": "",
                                    "godown_quantity": stock_info["quantity"],
                                    "godown_quantity_type": stock_info["type"],
                                    "use_item": [{
                                        "item_name": key,
                                        "item_category": common_category,
                                        "quantity": "",
                                    }],
                                    "total_quantity": "0",
                                })

            # Format the response
            formatted_response = [
                {"name": category, "data": items}
                for category, items in response_data.items()
            ]
            
            # Merge with existing data if needed
            if is_existing:
                consolidated_list = self.consolidate_categories(existing_list_data + formatted_response)
            else:
                consolidated_list = formatted_response
                
            # Update or create the event ingredient list
            event_ingredient_list, created = EventIngridientList.objects.update_or_create(
                event_id=event_id,
                defaults={"ingridient_list_data": consolidated_list},
            )
            
            return Response(
                {
                    "status": True,
                    "message": "Ingredients analysis completed",
                    "data": consolidated_list,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": False, "message": str(e)}, 
                status=status.HTTP_200_OK,
            )
