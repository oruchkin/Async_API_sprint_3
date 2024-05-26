from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.postgres.aggregates import ArrayAgg
from django.http import JsonResponse, Http404
from django.views.generic.list import BaseListView
from movies.models import Filmwork, RoleType


class MoviesApiMixin(BaseListView):
    model = Filmwork
    http_method_names = ['get']

    def annotate_filmwork(self, queryset):
        return queryset.annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg(
                'personfilmwork__person__full_name',
                filter=Q(personfilmwork__role=RoleType.ACTOR),
                distinct=True
            ),
            directors=ArrayAgg(
                'personfilmwork__person__full_name',
                filter=Q(personfilmwork__role=RoleType.DIRECTOR),
                distinct=True
            ),
            writers=ArrayAgg(
                'personfilmwork__person__full_name',
                filter=Q(personfilmwork__role=RoleType.WRITER),
                distinct=True
            ),
        )

    def get_queryset(self):
        queryset = Filmwork.objects.values(
            'id', 'title', 'description', 'creation_date', 'rating', 'type'
        )
        return self.annotate_filmwork(queryset)

    def get_object(self):
        return Filmwork.objects.filter(pk=self.kwargs['pk']).values(
            'id', 'title', 'description', 'creation_date', 'rating', 'type'
        ).annotate(
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg(
                'personfilmwork__person__full_name',
                filter=Q(personfilmwork__role=RoleType.ACTOR),
                distinct=True
            ),
            directors=ArrayAgg(
                'personfilmwork__person__full_name',
                filter=Q(personfilmwork__role=RoleType.DIRECTOR),
                distinct=True
            ),
            writers=ArrayAgg(
                'personfilmwork__person__full_name',
                filter=Q(personfilmwork__role=RoleType.WRITER),
                distinct=True
            ),
        ).first()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page', 1)

        if page_number == 'last':
            page_number = paginator.num_pages

        page = paginator.get_page(page_number)

        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(page.object_list),
        }
        return context


class MoviesDetailApi(MoviesApiMixin):
    def get_context_data(self, **kwargs):
        pk = kwargs.get('pk')
        return self.get_object(pk)


class MoviesListApi(MoviesApiMixin):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page', 1)

        if page_number == 'last':
            page_number = paginator.num_pages

        page = paginator.get_page(page_number)

        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(page.object_list),
        }
        return context


class MoviesDetailApi(MoviesApiMixin):
    def get_context_data(self, **kwargs):
        return self.get_object()
