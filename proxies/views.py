import logging
import ssl
import time

import requests
from requests.auth import HTTPProxyAuth
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from proxies.models import Proxy
from proxies.serializers import ProxySerializer

# Create your views here.
logger = logging.getLogger(__name__)

class ProxiesView(viewsets.ModelViewSet):
    serializer_class = ProxySerializer
    queryset = Proxy.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="create-proxy")
    def create_proxy(self, request):
        try:
            user = request.user.id
            request.data["user"] = user
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="get-all-proxy")
    def get_all_proxy(self, request):
        try:
            user = request.user.id
            proxy = Proxy.objects.filter(user=user)
            serializer = self.get_serializer(proxy, many=True)
            if proxy:
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response("No proxy found!", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="create-proxy/<uuid:proxy_id>")
    def get_proxy(self, request, proxy_id):
        try:
            proxy = Proxy.objects.get(id=proxy_id)
            if not proxy:
                return Response("Proxy not found!", status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(proxy)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["patch"], url_path="update-proxy/<uuid:proxy_id>")
    def update_proxy(self, request, proxy_id):
        try:
            proxy = Proxy.objects.get(id=proxy_id)
            if not proxy:
                return Response("Proxy not found!", status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(proxy, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["patch"], url_path="test_proxy/<uuid:proxy_id>")
    def test_proxy_connection(self, request, proxy_id):
        test_url = "https://api.gotinder.com"
        try:
            proxy = Proxy.objects.get(id=proxy_id)
            if not proxy:
                return Response("Proxy not found!", status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(proxy)
            proxy_data = serializer.data
            proxies = {}
            if proxy_data["type"] == "HTTP":
                proxies = {
                    "http": f"https://{proxy_data['host']}:{proxy_data['port']}",
                    "https": f"https://{proxy_data['host']}:{proxy_data['port']}",
                }
            elif proxy_data["type"] == "SOCKS5":
                proxies = {
                    "http": f"socks5://{proxy_data['host']}:{proxy_data['port']}",
                    "https": f"socks5://{proxy_data['host']}:{proxy_data['port']}",
                }

            auth = HTTPProxyAuth(proxy_data["username"], proxy_data["password"])
            print(proxies)
            print(auth.username, auth.password)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            for attempt in range(3):
                try:
                    response = requests.get(test_url, proxies=proxies, auth=auth, timeout=40, verify=False)
                    if response.status_code == 200:
                        proxy.status = "Active"
                        proxy.save()
                        return Response("Proxy connection successful!", status=status.HTTP_200_OK)
                    else:
                        proxy.status = "Inactive"
                        proxy.save()
                        return Response("Proxy connection failed!", status=status.HTTP_400_BAD_REQUEST)
                except requests.exceptions.RequestException as e:
                    logging.error(f"RequestException during proxy test: {str(e)}")
                    if attempt == 2:
                        return Response(f"RequestException: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    time.sleep(5)

        except Exception as e:
            return Response(f"Exception: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["delete"], url_path="delete-proxy/<uuid:proxy_id>")
    def delete_proxy(self, request, proxy_id):
        try:
            proxy = Proxy.objects.get(id=proxy_id)
            if not proxy:
                return Response("Proxy not found!", status=status.HTTP_400_BAD_REQUEST)
            proxy.delete()
            return Response("Proxy deleted successfully!", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
