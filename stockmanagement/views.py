from rest_framework.response import Response
from rest_framework import status, generics
from trayza.Utils.permissions import *
from .serializers import *
from decimal import Decimal

# --------------------    StokeCategoryViewSet    --------------------


class StokeCategoryViewSet(generics.GenericAPIView):
    serializer_class = StokeCategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def post(self, request):
        if StokeCategory.objects.filter(name=request.data.get("name")).exists():
            return Response(
                {
                    "status": False,
                    "message": "Category already exists",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        serializer = StokeCategorySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Category created successfully",
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
        queryset = StokeCategory.objects.all()
        serializer = StokeCategorySerializer(queryset, many=True)
        return Response(
            {
                "status": True,
                "message": "Category list",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class EditeStokeCategoryViewSet(generics.GenericAPIView):
    serializer_class = StokeCategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def put(self, request, pk=None):
        try:
            category = StokeCategory.objects.get(pk=pk)
            serializer = StokeCategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Category updated successfully",
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
        except StokeCategory.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Category not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, pk=None):
        try:
            category = StokeCategory.objects.get(pk=pk)
            category.delete()
            return Response(
                {
                    "status": True,
                    "message": "Category deleted successfully",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        except StokeCategory.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Category not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def get(self, request, pk=None):
        try:
            category = StokeCategory.objects.get(pk=pk)
            serializer = StokeCategorySerializer(category)
            return Response(
                {
                    "status": True,
                    "message": "Category retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except StokeCategory.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Category not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )



# --------------------    StokeItemViewSet    --------------------


class StokeItemViewSet(generics.GenericAPIView):
    serializer_class = StokeItemSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get(self, request):
        queryset = StokeItem.objects.all()
        serializer = StokeItemSerializer(queryset, many=True)
        return Response(
            {
                "status": True,
                "message": "StokeItem list",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if StokeItem.objects.filter(name=request.data.get("name")).exists():
            return Response(
                {
                    "status": False,
                    "message": "StokeItem already exists",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        serializer = StokeItemSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "StokeItem created successfully",
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


class EditStokeItemViewSet(generics.GenericAPIView):
    serializer_class = StokeItemSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get(self, request, pk=None):
        try:
            stokeitem = StokeItem.objects.get(pk=pk)
            serializer = StokeItemSerializer(stokeitem)
            return Response(
                {
                    "status": True,
                    "message": "StokeItem retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except StokeItem.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "StokeItem not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def put(self, request, pk=None):
        try:
            stokeitem = StokeItem.objects.get(pk=pk)
            request.data["quantity"] = str(
                int(request.data["quantity"]) + int(stokeitem.quantity)
            )
            request.data["total_price"] = str(
                int(request.data["total_price"]) + int(stokeitem.total_price)
            )
            request.data["nte_price"] = str(
                int(int(request.data["total_price"]) / int(request.data["quantity"]))
            )
            serializer = StokeItemSerializer(stokeitem, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "StokeItem updated successfully",
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
        except StokeItem.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "StokeItem not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, pk=None):
        try:
            stokeitem = StokeItem.objects.get(pk=pk)
            stokeitem.delete()
            return Response(
                {
                    "status": True,
                    "message": "StokeItem deleted successfully",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        except StokeItem.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "StokeItem not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )


# --------------------    AddRemoveStokeItemViewSet    --------------------


class AddRemoveStokeItemViewSet(generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin]

    def post(self, request):
        if not StokeItem.objects.filter(
            id=request.data.get("id"), name=request.data.get("name")
        ).exists():
            return Response(
                {
                    "status": False,
                    "message": "StokeItem is not exists",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        quantity = request.data.get("quantity")
        nte_price = request.data.get("nte_price")
        total_price = request.data.get("total_price", None)
        price = ""
        stoke_item = StokeItem.objects.get(
            id=request.data.get("id"), name=request.data.get("name")
        )
        result = stoke_item.quantity - Decimal(quantity)
        if total_price:
            price = total_price
        else:
            price = str(int(quantity) * int(nte_price))
        stoke_item.total_price = str(int(stoke_item.total_price) - int(price))
        stoke_item.quantity = result
        stoke_item.save()
        return Response(
            {
                "status": True,
                "message": "StokeItem Quantity Remove successfully",
                "data": {
                    "id": stoke_item.id,
                    "name": stoke_item.name,
                    "quantity": str(stoke_item.quantity),
                    "nte_price": str(stoke_item.nte_price),
                    "total_price": str(stoke_item.total_price),
                },
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        if not StokeItem.objects.filter(
            id=request.data.get("id"), name=request.data.get("name")
        ).exists():
            return Response(
                {
                    "status": False,
                    "message": "StokeItem is not exists",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        quantity = request.data.get("quantity")
        total_price = request.data.get("total_price", None)
        stoke_item = StokeItem.objects.get(
            id=request.data.get("id"), name=request.data.get("name")
        )
        result = stoke_item.quantity + Decimal(quantity)
        stoke_item.quantity = result
        if total_price:
            stoke_item.total_price = str(int(stoke_item.total_price) + int(total_price))
            stoke_item.nte_price = str(
                int(int(stoke_item.total_price) / int(stoke_item.quantity))
            )
        else:
            total_price = str(int(quantity) * int(stoke_item.nte_price))
            stoke_item.total_price = int(int(stoke_item.total_price) + int(total_price))
            stoke_item.nte_price = str(
                int(int(stoke_item.total_price) / int(stoke_item.quantity))
            )
        stoke_item.save()
        return Response(
            {
                "status": True,
                "message": "StokeItem Quantity Added successfully",
                "data": {
                    "id": stoke_item.id,
                    "name": stoke_item.name,
                    "quantity": str(stoke_item.quantity),
                    "nte_price": str(stoke_item.nte_price),
                    "total_price": str(stoke_item.total_price),
                },
            },
            status=status.HTTP_200_OK,
        )


# --------------------    AlertstokeItemViewSet    --------------------


class AlertstokeItemViewSet(generics.GenericAPIView):
    permission_classes = [IsAdminUserOrReadOnly]

    def get(self, request):
        alerts_list = []
        all_stoke_itmes = StokeItem.objects.all()
        for stokes in all_stoke_itmes:
            if stokes.type == "KG":
                # value_in_kilograms = stokes.quantity / Decimal('1000')
                if stokes.quantity <= Decimal(stokes.alert.split(" ")[0]):
                    alerts_list.append(stokes)

            if stokes.type == "L":
                # liters = stokes.quantity / 1000
                if stokes.quantity <= Decimal(stokes.alert.split(" ")[0]):
                    alerts_list.append(stokes)

            if stokes.type == "QTY":
                if stokes.quantity <= Decimal(stokes.alert.split(" ")[0]):
                    alerts_list.append(stokes)

        serializer = StokeItemSerializer(alerts_list, many=True)

        return Response(
            {
                "status": True,
                "message": "StokeItem Quantity Added successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

