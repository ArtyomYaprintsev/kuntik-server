from rest_framework import pagination


class StandardPageNumberPagination(pagination.PageNumberPagination):
    """Extended `PageNumberPagination` with custom properties."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
