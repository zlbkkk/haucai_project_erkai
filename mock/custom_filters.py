from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

# 自定义搜索过滤器，替代rest_framework.filters.SearchFilter
class CustomSearchFilter(BaseFilterBackend):
    """
    自定义搜索过滤器，用于替代rest_framework.filters.SearchFilter
    """
    search_param = 'search'
    
    def get_search_terms(self, request):
        """
        从请求中获取搜索词
        """
        params = request.query_params.get(self.search_param, '')
        return params.replace(',', ' ').split()
    
    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)
        
        if not search_fields or not search_terms:
            return queryset
            
        orm_lookups = [
            self.construct_search(str(search_field))
            for search_field in search_fields
        ]
        
        base = queryset
        conditions = Q()
        for search_term in search_terms:
            queries = [
                Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions |= Q(*queries)
            
        return base.filter(conditions)
    
    def construct_search(self, field_name):
        return "%s__icontains" % field_name 