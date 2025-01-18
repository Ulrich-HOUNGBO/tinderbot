from uuid import UUID

from rest_framework import serializers

from proxies.models import Proxy
from strategies.models import Strategy


class StrategySerializer(serializers.ModelSerializer):
    proxy = serializers.PrimaryKeyRelatedField(
        queryset=Proxy.objects.all(), allow_null=True
    )

    class Meta:
        model = Strategy
        fields = "__all__"

    def validate_proxy(self, value):
        if value is None:
            return value  # Allow null proxy
        # Extract the ID from the Proxy object
        proxy_id = str(value.id) if isinstance(value, Proxy) else str(value)
        print(
            f"Proxy ID received: {proxy_id}"
        )  # Debug line to check the incoming value
        try:
            # Ensure the value is a valid UUID
            UUID(proxy_id)
        except ValueError:
            raise serializers.ValidationError("Invalid UUID format for proxy.")
        return value

    def update(self, instance, validated_data):
        proxy_data = validated_data.get("proxy", None)

        # Update other fields normally
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Assign the proxy if present
        if proxy_data:
            # If proxy_data is not a Proxy instance, fetch it
            if isinstance(proxy_data, str) or isinstance(proxy_data, UUID):
                try:
                    proxy_instance = Proxy.objects.get(id=proxy_data)
                    instance.proxy = proxy_instance
                except Proxy.DoesNotExist:
                    raise serializers.ValidationError("Proxy not found.")
            else:
                instance.proxy = proxy_data  # Assuming it's already a Proxy object

        instance.save()
        return instance
