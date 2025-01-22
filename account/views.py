import logging
from uuid import UUID

import pytz
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from account.models import Account
from account.serializers import AccountSerializer
from action.models import Action
from bot.helpers import TinderConfig
from bot.helpers.bot_service import BotService
from gpt import BioGenerator

logger = logging.getLogger(__name__)
# Create your views here.


class AccountViews(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="create_account")
    def create_account(self, request, *args, **kwargs):
        try:
            # Set the user from request
            user = request.user.id
            request.data["user"] = user

            if Account.objects.filter(title=request.data.get("title"), user=user).exists():
                return Response({"error": "You already have account with same name"}, status=status.HTTP_400_BAD_REQUEST)

            # Handle strategy validation
            strategy = request.data.get("strategy")
            if strategy:
                try:
                    # Ensure the strategy is a valid UUID if it's not null
                    UUID(str(strategy))
                except ValueError:
                    return Response(
                        {"strategy": ["Invalid data. Expected a valid UUID."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            elif strategy is None:
                request.data["strategy"] = None  # Allow null strategy if needed
            # Validate and save the account data
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="get_all_account")
    def get_all_account(self, request, *args, **kwargs):
        try:
            user = request.user.id
            accounts = Account.objects.filter(user=user)
            serializer = self.get_serializer(accounts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="get_account/<uuid:account_id>")
    def get_account(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id)
            if not account:
                return Response(
                    "Account not found!", status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False, methods=["patch"], url_path="update_account/<uuid:account_id>"
    )
    def update_account(self, request, account_id, *args, **kwargs):
        try:
            account = Account.objects.get(id=account_id)
            if not account:
                return Response(
                    "Account not found!", status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure strategy is a valid UUID
            strategy = request.data.get("strategy")
            if strategy:
                try:
                    UUID(str(strategy))
                except ValueError:
                    return Response(
                        {"strategy": ["Invalid data. Expected a valid UUID."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                # Check if the strategy has changed
                if str(account.strategy) != strategy:
                    account.progress = 1  # Reset progress to 1

            distance_filter = request.data.get("distance")
            age_filter_min = request.data.get("min_age")
            age_filter_max = request.data.get("max_age")
            if distance_filter or age_filter_min or age_filter_max:
                token = account.token
                tinder_config = TinderConfig(token)
                result = tinder_config.update_profile(
                    distance_filter=distance_filter,
                    age_filter_min=age_filter_min,
                    age_filter_max=age_filter_max,
                )
                print(result)

            serializer = self.get_serializer(account, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False, methods=["delete"], url_path="delete_account/<uuid:account_id>"
    )
    def delete_account(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id)
            if not account:
                return Response(
                    "Account not found!", status=status.HTTP_400_BAD_REQUEST
                )
            account.delete()
            return Response("Account deleted successfully!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["patch"], url_path="start_process/<uuid:account_id>")
    def start_process(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id)
            if not account.strategy:
                return Response(
                    "Account doesn't have a strategy to start the process",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            account.status = "active"
            account.save()

            return Response("Process started successfully!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, method=["patch"], url_path="reset_process/<uuid:account_id>")
    def reset_process(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id)
            account.process_day = 1
            account.save()
            return Response("Process reset successfully!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, method=["get"], url_path="automate_all_account_process")
    def automate_all_account_process(self):

        try:
            accounts = Account.objects.filter(Q(status="active") | Q(status="working"))
            logger.info(f'Accounts: {accounts}')
            for account in accounts:
                if account.strategy is not None:
                    logger.info(f'Account strategy: {account.strategy}')
                    # Get all actions for the strategy
                    logger.info(f'Account strategy ID: {account.strategy.id}')
                    bot_settings = Action.objects.filter(strategy=account.strategy.id)
                    logger.info(f'Bot settings count: {bot_settings.count()}')

                    # Log the actual BotSettings objects
                    for bot_setting in bot_settings:
                        logger.info(f'Bot setting: {bot_setting}')
                        account_timezone = pytz.timezone(account.timezone_field)
                        current_time = timezone.now().astimezone(account_timezone).time()
                        current_hour_minute = current_time.replace(second=0, microsecond=0)
                        if (
                                bot_setting.related_day == account.progress and
                                (bot_setting.scheduled_time == current_hour_minute or
                                 bot_setting.scheduled_time_2 == current_hour_minute)

                        ):
                            # Use individual BotSetting to start the bot
                            logger.info(f'Account process day: {account.progress}')
                            bot_service = BotService(
                                token=account.token,
                                refresh_token=account.refresh_token,
                                device_id=account.device_id,
                            )

                            response = bot_service.automate_swipes_task(
                                min_swipes=bot_setting.min_swipe_times,
                                max_swipes=bot_setting.max_swipe_times,
                                min_right_swipe_percentage=bot_setting.min_right_swipe_percentage,
                                max_right_swipe_percentage=bot_setting.max_right_swipe_percentage
                            )
                            logger.info(f'Response: {response}')
                            # Update account status based on the bot_service request status_code

                            if (
                                    response == "Error during swipe task: Failed to fetch recommendations: 401"
                            ):
                                account.status = "failed"
                                print(f'account_status', account.status)
                            elif (
                                    "error" in response
                                    and response["error"] == "Failed to fetch recommendations."
                            ):
                                account.status = "shadowban"
                                print(f'account_status', account.status)
                            else:
                                account.status = "working"
                                print(f'account_status', account.status)
                            account.save()

            return Response("Process started successfully!", status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f'Error in automate_all_account_process: {e}')
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, method=["patch"], url_path="stop_process/<uuid:account_id>")
    def stop_process(self, request, account_id):
            try:
                account = Account.objects.get(id=account_id)
                account.status = "standby"
                account.save()
                return Response("Process stopped successfully!", status=status.HTTP_200_OK)
            except Exception as e:
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, method=["post"], url_path="test-account/<uuid:account_id>")
    def test_account(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id)
            if not account:
                return Response(
                    "Account not found!", status=status.HTTP_400_BAD_REQUEST
                )
            bot_service = BotService(
                token=account.token,
                refresh_token=account.refresh_token,
                device_id=account.device_id,
            )
            response = bot_service.connect_tinder()
            if "error" in response:
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            return Response("Account connection successful!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_process_day(self, *args, **kwargs):
        try:
            accounts = Account.objects.filter(status="working")
            for account in accounts:
                if account.progress == account.strategy.days_number:
                    account.status = "completed"
                    account.save()
                else:
                    account.progress += 1
                    account.save()
            return Response("Accounts updated successfully")
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["patch"], url_path="add_bio/<uuid:account_id>")
    def add_bio(self, account_id, description):
        try:
            account = Account.objects.get(id=account_id)
            bot_service = BotService(
                token=account.token,
                refresh_token=account.refresh_token,
                device_id=account.device_id,
            )
            bot_service.addBioagraphie(description)
            account.save()
            return Response("Description added successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def automate_bio_strategy(self, *args, **kwargs):
        try:
            accounts = Account.objects.filter(status="active")
            for account in accounts:
                if account.strategy is not None:
                    actions = Action.objects.filter(strategy=account.strategy.id)
                    for action in actions:
                        if account.strategy.type == "add-bio" and account.progress == action.related_day:
                            bio_generator = BioGenerator(account.strategy.api_key)
                            bio = bio_generator.generate_bio(account.strategy.bio_examples)
                            logger.info(f'Generated bio: {bio}')
                            tinder_bio = TinderConfig(account.token)
                            tinder_bio.update_profile(bio)
                            account.save()
            return Response("Bio strategy automated successfully", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
