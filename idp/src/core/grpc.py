import logging
from concurrent import futures
from uuid import UUID

import grpc
import grpc.experimental
import grpc_api.user_info_pb2 as user_info_pb2
import grpc_api.user_info_pb2_grpc as user_info_server
from services.keycloak_client import get_keycloak_service
from services.oidc_client import get_oidc_service

logging.basicConfig(level=logging.DEBUG)


class UserInfoServicer(user_info_server.UserInfoServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        oidc = get_oidc_service()
        self._keycloak = get_keycloak_service(oidc)
        pass

    async def GetUser(self, request: user_info_pb2.GetUserRequest, context):
        self._logger.info("Getting user info %s", request)
        user = await self._keycloak.get_user(UUID(request.id))
        self._logger.info("Got user info %s", user.id)
        return user_info_pb2.Info(id=str(user.id), email=user.email)

    async def GetAllUsers(self, request_iterator, context):
        for req in request_iterator:
            user = await self._keycloak.get_user(UUID(req.id))
            yield user_info_pb2.Info(id=str(user.id), email=user.email)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_info_server.add_UserInfoServicer_to_server(UserInfoServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


async def start_grpc():
    logging.basicConfig(level=logging.DEBUG)
    server = grpc.aio.server()
    user_info_server.add_UserInfoServicer_to_server(UserInfoServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.add_insecure_port("0.0.0.0:50051")
    await server.start()
    await server.wait_for_termination()
