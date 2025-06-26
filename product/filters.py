import django_filters
from .models import Brand, Category, Size, Product


class BrandFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    has_categories = django_filters.BooleanFilter(method="filter_has_categories")
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(), method="filter_by_category"
    )

    class Meta:
        model = Brand
        fields = ["name", "has_categories", "category"]

    def filter_has_categories(self, queryset, name, value):
        if value:
            return queryset.filter(brand_categories__isnull=False).distinct()
        return queryset.filter(brand_categories__isnull=True)

    def filter_by_category(self, queryset, name, value):
        return queryset.filter(brand_categories__category=value).distinct()


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    slug = django_filters.CharFilter(lookup_expr="icontains")
    has_parent = django_filters.BooleanFilter(method="filter_has_parent")
    has_children = django_filters.BooleanFilter(method="filter_has_children")
    has_brands = django_filters.BooleanFilter(method="filter_has_brands")
    level = django_filters.NumberFilter(method="filter_by_level")

    class Meta:
        model = Category
        fields = [
            "name",
            "slug",
            "parent",
            "has_parent",
            "has_children",
            "has_brands",
            "level",
        ]

    def filter_has_parent(self, queryset, name, value):
        if value:
            return queryset.filter(parent__isnull=False)
        return queryset.filter(parent__isnull=True)

    def filter_has_children(self, queryset, name, value):
        if value:
            return queryset.filter(children__isnull=False).distinct()
        return queryset.filter(children__isnull=True)

    def filter_has_brands(self, queryset, name, value):
        if value:
            return queryset.filter(category_brands__isnull=False).distinct()
        return queryset.filter(category_brands__isnull=True)

    def filter_by_level(self, queryset, name, value):
        # This is a simplified level filter - you might need to adjust based on your needs
        if value == 0:
            return queryset.filter(parent__isnull=True)
        elif value == 1:
            return queryset.filter(parent__isnull=False, parent__parent__isnull=True)
        # Add more levels as needed
        return queryset


class SizeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    brand_name = django_filters.CharFilter(
        field_name="brand__name", lookup_expr="icontains"
    )
    category_name = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )
    category_slug = django_filters.CharFilter(
        field_name="category__slug", lookup_expr="icontains"
    )

    class Meta:
        model = Size
        fields = [
            "name",
            "brand",
            "category",
            "brand_name",
            "category_name",
            "category_slug",
        ]


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    brand = django_filters.CharFilter(field_name="brand__name", lookup_expr="icontains")
    category = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )
    size = django_filters.CharFilter(field_name="size__name", lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ["brand", "category", "size", "is_archived"]
