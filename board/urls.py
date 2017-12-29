from django.conf.urls import url
from . import views

app_name = 'board'

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^create/$', views.ScoreboardCreate.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/$', views.ScoreboardView.as_view(), name="scoreboard"),
    # /board/[board_id]/get_changes/ AJAX GET call from scoreboard
    url(r'^(?P<pk>[0-9]+)/get_changes/$', views.GetChanges.as_view(),
        name="get_changes"),
    url(r'^(?P<pk>[0-9]+)/query/$', views.QueryView.as_view(), name="query"),
    url(r'^(?P<pk>[0-9]+)/manager/$', views.ManagerView.as_view(), name="manager"),
    url(r'^(?P<pk>[0-9]+)/set_theme/$', views.ThemeQuery.as_view(),
        name="set_theme"),
    url(r'^(?P<pk>[0-9]+)/fix_overflow/$', views.OverflowQuery.as_view(),
        name="fix_overflow"),
    url(r'^(?P<pk>[0-9]+)/win_animation/$', views.WinQuery.as_view(),
        name="win_animation"),
    url(r'^(?P<pk>[0-9]+)/gain_loss_animation/$', views.GainLossQuery.as_view(),
        name="gain_loss_animation"),
    url(r'^(?P<pk>[0-9]+)/points_change/$', views.PointsChangeQuery.as_view(),
        name="points_change"),
    url(r'^(?P<pk>[0-9]+)/question/$', views.QuestionQuery.as_view(),
        name="question"),
    url(r'^(?P<pk>[0-9]+)/save_pcs/$', views.SavePointsQuery.as_view(),
        name="save_pcs"),
    url(r'^(?P<pk>[0-9]+)/undo/$', views.UndoQuery.as_view(),
        name="undo"),
    url(r'^(?P<pk>[0-9]+)/recalculate/$', views.RecalculateQuery.as_view(),
        name="recalculate"),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.ScoreboardDelete.as_view(),
        name="delete"),

]
