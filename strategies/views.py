from uuid import UUID

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from strategies.models import Strategy
from strategies.serializer import StrategySerializer


# Create your views here.


class StrategyViews(viewsets.ModelViewSet):
    serializer_class = StrategySerializer
    queryset = Strategy.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="create_strategy")
    def create_strategy(self, request, *args, **kwargs):
        try:
            user = request.user.id
            request.data["user"] = user
            proxy = request.data.get("proxy")
            if proxy:
                try:
                    UUID(str(proxy))
                except ValueError:
                    return Response(
                        {"proxy": ["Invalid data. Expected a valid UUID."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif proxy is None:
                request.data["proxy"] = None

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="get_all_strategy")
    def get_all_strategy(self, request, *args, **kwargs):
        try:
            user = request.user.id
            strategies = Strategy.objects.filter(user=user)
            serializer = self.get_serializer(strategies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="get_strategy/<uuid:strategy_id>")
    def get_strategy(self, request, strategy_id, *args, **kwargs):
        try:
            strategy = Strategy.objects.get(id=strategy_id)
            if not strategy:
                return Response(
                    "Strategy not found!", status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(strategy)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False, methods=["patch"], url_path="update_strategy/<uuid:strategy_id>"
    )
    def update_strategy(self, request, strategy_id, *args, **kwargs):
        try:
            strategy = Strategy.objects.get(id=strategy_id)
            if not strategy:
                return Response(
                    "Strategy not found!", status=status.HTTP_400_BAD_REQUEST
                )

            # Extract proxy_id if present and set it in the request data
            proxy = request.data.get("proxy")
            if proxy:
                request.data["proxy"] = str(proxy)  # Ensure proxy is a string

            serializer = self.get_serializer(strategy, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False, methods=["delete"], url_path="delete_strategy/<uuid:strategy_id>"
    )
    def delete_strategy(self, request, strategy_id, *args, **kwargs):
        try:
            strategy = Strategy.objects.get(id=strategy_id)
            if not strategy:
                return Response(
                    "Strategy not found!", status=status.HTTP_400_BAD_REQUEST
                )
            strategy.delete()
            return Response("Strategy deleted!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
