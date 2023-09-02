from rest_framework.authentication import TokenAuthentication


class BearerAuthentication(TokenAuthentication):
    """Token authentication with the `Bearer` keyword."""

    keyword = "Bearer"
