from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomLimitOffsetPagination(LimitOffsetPagination):

    def get_paginated_response(self, data):
        return Response({
            "count": self.count,
            "limit": self.limit,
            "offset": self.offset,
            "previous": self.get_previous_link(),
            "next": self.get_next_link(),
            "results": data
        })
