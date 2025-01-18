from absl.app import usage
from django.db.models import Count
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from modeles import models
from modeles.models import Modeles
from modeles.serializer import ModeleSerializer


# Create your views here.


class ModelesView(viewsets.ModelViewSet):
    serializer_class = ModeleSerializer
    queryset = Modeles.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="create-modele")
    def create_modele(self, request):
        try:
            user = request.user.id
            request.data["user"] = user

            # Check if model n ame already exists
            if Modeles.objects.filter(name=request.data.get("name"), user=user).exists():
                return Response({"error": "Model name already exists"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="get-all-modele")
    def get_all_modele(self, request):
        try:
            modeles = Modeles.objects.filter(user=request.user.id).annotate(account_count=Count('account'))
            serializer = self.get_serializer(modeles, many=True)
            if modeles:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response("No modeles found!", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="get-modele/<uuid:modele_id>")
    def get_modele(self, request, modele_id):
        try:
            modele = Modeles.objects.get(id=modele_id)
            if not modele:
                return Response("Modele not found!", status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(modele)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["patch"], url_path="update-modele/<uuid:modele_id>")
    def update_modele(self, request, modele_id):
        try:
            modele = Modeles.objects.get(id=modele_id)
            if not modele:
                return Response("Modele not found!", status=status.HTTP_400_BAD_REQUEST)

            # Check if new model name already exists
            new_name = request.data.get("name")
            if new_name and Modeles.objects.filter(name=new_name, user=request.user.id).exists():
                return Response({"error": "Model name already exists"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(modele, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["delete"], url_path="delete-modele/<uuid:modele_id>")
    def delete_modele(self, request, modele_id):
        try:
            modele = Modeles.objects.get(id=modele_id)
            if not modele:
                return Response("Modele not found!", status=status.HTTP_400_BAD_REQUEST)
            modele.delete()
            return Response("Modele deleted successfully!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
