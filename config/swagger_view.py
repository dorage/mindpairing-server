from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Mindpairing API",
        default_version='v0',
        description="마링 API 문서",
        # terms_of_service="https://www.example.com/policies/terms/",
        # contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

def swagger_view(request):
    return schema_view.with_ui('swagger')(request)