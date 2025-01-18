from rest_framework import serializers

from action.models import Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
