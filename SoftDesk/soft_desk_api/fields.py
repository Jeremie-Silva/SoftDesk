from rest_framework.serializers import Field, ValidationError
from .models import Contributor


class ContributorField(Field):
    def to_internal_value(self, data):
        if isinstance(data, int) or data.isdigit():  # is int or str contains digit
            try:
                return Contributor.objects.get(pk=int(data))
            except Contributor.DoesNotExist:
                raise ValidationError(f"Contributor with ID {data} does not exist.")
        else:  # is str
            try:
                return Contributor.objects.get(user__username=data)
            except Contributor.DoesNotExist:
                raise ValidationError(f"Contributor with username {data} does not exist.")

    def to_representation(self, value):
        return value.user.username
