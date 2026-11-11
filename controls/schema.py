import graphene
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.translation import gettext as _

from core import ExtendedConnection
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Control

class ControlGQLType(DjangoObjectType):
    class Meta:
        model = Control
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'adjustability': ['exact', 'icontains', 'istartswith'],
            'usage': ['exact', 'icontains', 'istartswith'],
        }
        connection_class = ExtendedConnection

def check_authenticated(info):
    """The field controls are read by the logged-in apps only (not anonymously)."""
    user = getattr(getattr(info, "context", None), "user", None)
    if user is None or getattr(user, "is_anonymous", True) or not getattr(user, "id", None):
        raise PermissionDenied(_("unauthorized"))
    return user


class Query(graphene.ObjectType):
    control = DjangoFilterConnectionField(ControlGQLType)
    control_str = DjangoFilterConnectionField(
        ControlGQLType,
        str = graphene.String()
    )

    def resolve_control(self, info, **kwargs):
        check_authenticated(info)
        return Control.objects.all()

    def resolve_control_str(self, info, **kwargs):
        check_authenticated(info)
        search_str = kwargs.get('str')
        if search_str is not None:
            return Control.objects \
                .filter(Q(adjustability__icontains=search_str) | Q(name__icontains=search_str) | Q(usage__icontains=search_str))
        else:
            return Control.objects
