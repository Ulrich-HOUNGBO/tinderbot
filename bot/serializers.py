from rest_framework import serializers

from bot.models import BotSettings
from strategies.serializer import StrategySerializer


class BotSettingsSerializer(serializers.ModelSerializer):

    strategy_details = StrategySerializer(source="strategy", read_only=True)

    class Meta:
        model = BotSettings
        fields = "__all__"
