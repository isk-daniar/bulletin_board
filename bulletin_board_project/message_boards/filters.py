import django_filters
from django.forms import DateInput
from django_filters import FilterSet

from .models import Post, Response


class ResponseFilter(FilterSet):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('my_user_id', None)
        super(ResponseFilter, self).__init__(*args, **kwargs)

        self.filters['post'].extra.update({
            'queryset': Post.objects.filter(user=self.user),
            'help_text': False
        })

    created_at = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gt',
        widget=DateInput(attrs={'type': 'date'},),
        label='Начиная с даты:',
    )

    post = django_filters.ModelChoiceFilter(
        field_name='post',
        label='Объявление:'
    )

    text = django_filters.CharFilter(
        field_name='text',
        label='Текст отклика',
        lookup_expr='icontains',
    )

    class Meta:
        model = Response
        fields = ('__all__')

