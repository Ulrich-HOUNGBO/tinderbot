from rest_framework import serializers

from proxies.models import Proxy


class ProxySerializer(serializers.ModelSerializer):
    class Meta:
        model = Proxy
        fields = "__all__"
