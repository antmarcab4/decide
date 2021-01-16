from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    re_path(r'^question/(?P<pk>\d+)/delete',views.QuestionDelete.as_view(), name='delete_question'),
]
