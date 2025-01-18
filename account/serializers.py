from uuid import UUID

from rest_framework import serializers

from account.models import Account
from modeles.models import Modeles
from strategies.models import Strategy


class AccountSerializer(serializers.ModelSerializer):
    strategy = serializers.PrimaryKeyRelatedField(
        queryset=Strategy.objects.all(), allow_null=True, required=False
    )

    modele = serializers.PrimaryKeyRelatedField(
        queryset=Modeles.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Account
        fields = "__all__"

    def validate_strategy(self, value):
        if value is None:
            return value  # Allow null strategy
        strategy_id = str(value.id) if isinstance(value, Strategy) else str(value)
        print(f"Strategy ID received: {strategy_id}")
        try:
            UUID(strategy_id)  # Ensure the value is a valid UUID
        except ValueError:
            raise serializers.ValidationError("Invalid UUID format for strategy.")
        return value

    def validate_model(self, value):
        if value is None:
            return value
        modele_id = str(value.id) if isinstance(value, Modeles) else str(value)
        print(f"Model ID received: {modele_id}")
        try:
            UUID(modele_id)
        except ValueError:
            raise serializers.ValidationError("Invalid UUID format for model.")

    def update(self, instance, validated_data):
        strategy_data = validated_data.pop("strategy", None)
        model_data = validated_data.pop("modele", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if strategy_data:
            if isinstance(strategy_data, str) or isinstance(strategy_data, UUID):
                try:
                    strategy_instance = Strategy.objects.get(id=strategy_data)
                    instance.strategy = strategy_instance
                except Strategy.DoesNotExist:
                    raise serializers.ValidationError("Strategy not found.")
            else:
                instance.strategy = strategy_data
        if model_data:
            if isinstance(model_data, str) or isinstance(model_data, UUID):
                try:
                    model_instance = Modeles.objects.get(id=model_data)
                    instance.modele = model_instance
                except Modeles.DoesNotExist:
                    raise serializers.ValidationError("Model not found.")
            else:
                instance.modele = model_data

        instance.save()
        return instance
