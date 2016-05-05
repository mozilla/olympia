from django.conf.urls import url

from olympia.addons.urls import ADDON_ID
from olympia.editors import views, views_themes


# All URLs under /editors/
urlpatterns = (
    url(r'^$', views.home, name='editors.home'),
    url(r'^queue$', views.queue, name='editors.queue'),
    url(r'^queue/nominated$', views.queue_nominated,
        name='editors.queue_nominated'),
    url(r'^queue/pending$', views.queue_pending,
        name='editors.queue_pending'),
    url(r'^queue/preliminary$', views.queue_prelim,
        name='editors.queue_prelim'),
    url(r'^queue/fast$', views.queue_fast_track,
        name='editors.queue_fast_track'),
    url(r'^queue/reviews$', views.queue_moderated,
        name='editors.queue_moderated'),
    url(r'^queue/application_versions\.json$', views.application_versions_json,
        name='editors.application_versions_json'),
    url(r'^unlisted_queue$', views.unlisted_queue,
        name='editors.unlisted_queue'),
    url(r'^unlisted_queue/nominated$', views.unlisted_queue_nominated,
        name='editors.unlisted_queue_nominated'),
    url(r'^unlisted_queue/pending$', views.unlisted_queue_pending,
        name='editors.unlisted_queue_pending'),
    url(r'^unlisted_queue/preliminary$', views.unlisted_queue_prelim,
        name='editors.unlisted_queue_prelim'),
    url(r'^unlisted_queue/all$', views.unlisted_list,
        name='editors.unlisted_queue_all'),
    url(r'^logs$', views.eventlog, name='editors.eventlog'),
    url(r'^log/(\d+)$', views.eventlog_detail, name='editors.eventlog.detail'),
    url(r'^reviewlog$', views.reviewlog, name='editors.reviewlog'),
    url(r'^beta_signed_log$', views.beta_signed_log,
        name='editors.beta_signed_log'),
    url(r'^queue_version_notes/%s?$' % ADDON_ID, views.queue_version_notes,
        name='editors.queue_version_notes'),
    url(r'^queue_review_text/(\d+)?$', views.queue_review_text,
        name='editors.queue_review_text'),  # (?P<addon_id>[^/<>"']+)
    url(r'^queue_viewing$', views.queue_viewing,
        name='editors.queue_viewing'),
    url(r'^review_viewing$', views.review_viewing,
        name='editors.review_viewing'),
    url(r'^review/%s$' % ADDON_ID, views.review, name='editors.review'),
    url(r'^performance/(?P<user_id>\d+)?$', views.performance,
        name='editors.performance'),
    url(r'^motd$', views.motd, name='editors.motd'),
    url(r'^motd/save$', views.save_motd, name='editors.save_motd'),
    url(r'^abuse-reports/%s$' % ADDON_ID, views.abuse_reports,
        name='editors.abuse_reports'),
    url(r'^leaderboard/$', views.leaderboard, name='editors.leaderboard'),
    url(r'^whiteboard/%s$' % ADDON_ID, views.whiteboard,
        name='editors.whiteboard'),

    url('^themes$', views_themes.home,
        name='editors.themes.home'),
    url('^themes/pending$', views_themes.themes_list,
        name='editors.themes.list'),
    url('^themes/flagged$', views_themes.themes_list,
        name='editors.themes.list_flagged',
        kwargs={'flagged': True}),
    url('^themes/updates$', views_themes.themes_list,
        name='editors.themes.list_rereview',
        kwargs={'rereview': True}),
    url('^themes/queue/$', views_themes.themes_queue,
        name='editors.themes.queue_themes'),
    url('^themes/queue/flagged$', views_themes.themes_queue_flagged,
        name='editors.themes.queue_flagged'),
    url('^themes/queue/updates$', views_themes.themes_queue_rereview,
        name='editors.themes.queue_rereview'),
    url('^themes/queue/commit$', views_themes.themes_commit,
        name='editors.themes.commit'),
    url('^themes/queue/single/(?P<slug>[^ /]+)$', views_themes.themes_single,
        name='editors.themes.single'),
    url('^themes/history/(?P<username>[^ /]+)?$',
        views_themes.themes_history, name='editors.themes.history'),
    url(r'^themes/logs$', views_themes.themes_logs,
        name='editors.themes.logs'),
    url('^themes/release$', views_themes.release_locks,
        name='editors.themes.release_locks'),
    url('^themes/logs/deleted/$', views_themes.deleted_themes,
        name='editors.themes.deleted'),
    url('^themes/search/$', views_themes.themes_search,
        name='editors.themes.search'),
)
