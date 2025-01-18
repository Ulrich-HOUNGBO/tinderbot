from rest_framework import serializers

from modeles.models import Modeles


class ModeleSerializer(serializers.ModelSerializer):
    account_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Modeles
        fields = '__all__'
