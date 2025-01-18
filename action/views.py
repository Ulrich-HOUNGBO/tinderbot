import uuid
from datetime import time

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from action.models import Action
from action.serializers import ActionSerializer


# Create your views here.

class ActionListView(viewsets.ModelViewSet):
    model = Action
    serializer_class = ActionSerializer
    queryset = Action.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="get-action")
    def ge_all_action(self, request, *args, **kwargs):
        try:
            actions = Action.objects.all()
            serializer = ActionSerializer(actions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["patch"], url_path="create-action")
    def create_action(self, request, *args, **kwargs):
        try:
            user = request.user.id
            request.data["user"] = user

            # Ensure strategy is a valid UUID
            strategy_id = request.data.get("strategy")
            if strategy_id:
                try:
                    uuid.UUID(str(strategy_id))
                except ValueError:
                    return Response(
                        {"strategy": ["Invalid data. Expected a valid UUID."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Get all the bot settings data by strategy id
            actions = Action.objects.filter(strategy_id=strategy_id)
            if actions:
                # Delete all the bot settings data by strategy id
                actions.delete()

            # Process bot settings
            actions_data = request.data.get("actions", [])
            created_settings = []
            for action_data in actions_data:
                action_data["user"] = user
                action_data["strategy"] = strategy_id

                # Convert schedule_time and schedule_time_2 to time format
                if "schedule_time" in action_data:
                    action_data["schedule_time"] = time.fromisoformat(
                        action_data["schedule_time"]
                    )
                if "schedule_time_2" in action_data:
                    action_data["schedule_time_2"] = time.fromisoformat(
                        action_data["schedule_time_2"]
                    )

                serializer = ActionSerializer(data=action_data)
                if serializer.is_valid():
                    serializer.save()
                    created_settings.append(serializer.data)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(created_settings, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["patch"], url_path="get-action/<uuid:action_id>")
    def get_action(self, request, action_id):
        try:
            bot_action = Action.objects.get(id=action_id)
            serializer = ActionSerializer(bot_action)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["patch"], url_path="update-action/<uuid:action_id>")
    def update_action(self, request, action_id):
        try:
            bot_action = Action.objects.get(id=action_id)
            serializer = ActionSerializer(bot_action, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], url_path="delete-action/<uuid:action_id>")
    def delete_action(self, request, action_id):
        try:
            bot_action = Action.objects.get(id=action_id)
            bot_action.delete()
            return Response("Action deleted successfully!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="get-strategy-actions/<uuid:strategy_id>")
    def get_strategy_actions(self, request, strategy_id):
        try:
            actions = Action.objects.filter(strategy_id=strategy_id)
            serializer = ActionSerializer(actions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
