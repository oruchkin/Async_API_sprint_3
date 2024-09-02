from uuid import UUID

import grpc
import src.services.idp_grpc.user_info_pb2 as user_info_pb2
import src.services.idp_grpc.user_info_pb2_grpc as user_info_pb2_grpc
from src.core.settings import IDPSettings


class IDPClient:
    def __init__(self, settings: IDPSettings) -> None:
        self._settings = settings

    async def get_user(self, id: UUID):
        async with grpc.aio.insecure_channel(self._settings.grpc) as channel:
            stub = user_info_pb2_grpc.UserInfoStub(channel)
            request = user_info_pb2.GetUserRequest(id=str(id))
            response = await stub.GetUser(request)
            print(f"User Info: name: {response.name}")


def get_idp_client() -> IDPClient:
    settings = IDPSettings()
    return IDPClient(settings)
