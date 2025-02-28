from django.urls import path
from .views import run_script, stop_script, get_script_status, test_view

urlpatterns = [
    path('run-script/', run_script, name='run_script'),
    path('stop-script/', stop_script, name='stop_script'),
    path('script-status/', get_script_status, name='script_status'),
    path('test/', test_view, name='test'),
]