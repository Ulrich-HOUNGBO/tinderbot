import uuid
from datetime import time
from time import timezone

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from bot.helpers.bot_service import BotService
from bot.models import BotSettings
from bot.serializers import BotSettingsSerializer


# Create your views here.
class BotSettingsView(viewsets.ModelViewSet):
    queryset = BotSettings.objects.all()
    serializer_class = BotSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["patch"], url_path="create-settings")
    def create_settings(self, request, *args, **kwargs):
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

            # get all the bot settings data by strategy id
            bot_settings = BotSettings.objects.filter(strategy_id=strategy_id)
            if bot_settings:
                # delete all the bot settings data by strategy id
                bot_settings.delete()

            # Process bot settings
            bot_settings_data = request.data.get("bot_settings", [])
            created_settings = []
            for setting_data in bot_settings_data:
                setting_data["user"] = user
                setting_data["strategy"] = strategy_id

                # Convert schedule_time and schedule_time_2 to time format
                if "schedule_time" in setting_data:
                    setting_data["schedule_time"] = time.fromisoformat(
                        setting_data["schedule_time"]
                    )
                if "schedule_time_2" in setting_data:
                    setting_data["schedule_time_2"] = time.fromisoformat(
                        setting_data["schedule_time_2"]
                    )

                serializer = BotSettingsSerializer(data=setting_data)
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

    @action(
        detail=False, methods=["patch"], url_path="start_bot/<uuid:bot_settings_id>"
    )
    def start_bot(self, request, bot_settings_id):
        try:
            bot_settings = BotSettings.objects.get(id=bot_settings_id)
            if not bot_settings:
                return Response(
                    "Bot settings not found!", status=status.HTTP_400_BAD_REQUEST
                )

            proxy_host = bot_settings.proxy.host if bot_settings.proxy else None
            proxy_username = bot_settings.proxy.username if bot_settings.proxy else None
            proxy_password = bot_settings.proxy.password if bot_settings.proxy else None

            bot_service = BotService(
                bot_settings.min_swipe_times,
                bot_settings.max_swipe_times,
                bot_settings.min_right_swipe_percentage,
                bot_settings.max_right_swipe_percentage,
                bot_settings.token,
                proxy_host,
                proxy_username,
                proxy_password,
            )
            bot_settings.status = "Running"
            bot_settings.save()

            try:
                bot_service.automate_swipes_task(num_swipes=bot_settings.swipe_times)
                bot_settings.status = "Stopped"
                bot_settings.save()
            except Exception as e:
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response("Bot started successfully!", status=status.HTTP_200_OK)

        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"], url_path="stop-bot/<uuid:bot_settings_id>")
    def stop_bot(self, request, bot_settings_id):
        try:
            bot_settings = BotSettings.objects.get(id=bot_settings_id)
            bot_settings.status = "Stopped"
            bot_settings.save()
            return Response("Bot stopped successfully!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="get-settings")
    def get_settings(self, request):
        try:
            queryset = BotSettings.objects.all()
            serializer = BotSettingsSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False,
        methods=["get"],
        url_path="get-settings-strategy/<uuid:strategy_id>",
    )
    def get_settings_strategy(self, request, strategy_id):
        try:
            queryset = BotSettings.objects.filter(strategy_id=strategy_id)
            serializer = BotSettingsSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False,
        methods=["patch"],
        url_path="update-settings/<uuid:bot_settings_id>",
    )
    def update_settings(self, request, bot_settings_id):
        try:
            queryset = BotSettings.objects.get(id=bot_settings_id)
            serializer = BotSettingsSerializer(
                queryset, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False,
        methods=["delete"],
        url_path="delete-settings/<uuid:bot_settings_id>",
    )
    def delete_settings(self, request, bot_settings_id):
        try:
            bot_settings = BotSettings.objects.get(id=bot_settings_id)
            bot_settings.delete()
            return Response(
                "Bot settings deleted successfully!", status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def scheduled_starting_bot(self, request):
        try:
            queryset = BotSettings.objects.all()
            current_time = timezone.now()
            for bot in queryset:
                if bot.scheduled_time == current_time:
                    bot_service = BotService(
                        bot.swipe_times,
                        bot.right_swipe_percentage,
                        bot.token,
                        bot.proxy.host,
                        bot.proxy.username,
                        bot.proxy.password,
                    )
                    bot_service.automate_swipes_task(num_swipes=bot.swipe_times)
            return Response("Bots started successfully!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=["get"], url_path="get-tinder-auth-token")
    def get_tinder_auth_token(self, request):
        try:
            bot_service = BotService(
                min_swipes=0,
                max_swipes=0,
                min_right_swipe_percentage=0,
                max_right_swipe_percentage=0,
                token="5969575a-7c32-4044-adde-0b28df033a15",
            )
            token = bot_service.get_profile()
            return Response(token, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)