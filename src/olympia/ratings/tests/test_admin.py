from django.urls import reverse

from pyquery import PyQuery as pq

from olympia.addons.models import Addon
from olympia.amo.tests import TestCase, user_factory
from olympia.ratings.models import Rating
from olympia.users.models import UserProfile


class TestRatingAdmin(TestCase):
    fixtures = ['base/addon_3615', 'base/user_999']

    def setUp(self):
        self.addon = Addon.objects.get(pk=3615)
        self.rating = Rating.objects.create(
            addon=self.addon, body='Bär', rating=5, user=user_factory()
        )
        self.detail_url = reverse('admin:ratings_rating_change', args=(self.rating.pk,))
        self.list_url = reverse('admin:ratings_rating_changelist')
        self.delete_url = reverse('admin:ratings_rating_delete', args=(self.rating.pk,))
        self.user = UserProfile.objects.get(pk=999)

    def test_list(self):
        addon = Addon.objects.get(pk=3615)

        # Create a few more ratings.
        Rating.objects.create(
            addon=addon,
            user=user_factory(),
            rating=4,
            body='Lôrem ipsum dolor sit amet, per at melius fuisset '
            'invidunt, ea facete aperiam his. Et cum iusto detracto, '
            'nam atqui nostrum no, eum altera indoctum ad. Has ut duis '
            'tractatos laboramus, cum sale primis ei. Ius inimicus '
            'intellegebat ea, mollis expetendis usu ei. Cetero aeterno '
            'nostrud eu për.',
        )
        Rating.objects.create(addon=addon, body=None, rating=5, user=user_factory())
        # Create a reply.
        Rating.objects.create(
            addon=addon, user=self.user, body='Réply', reply_to=self.rating
        )

        self.grant_permission(self.user, 'Ratings:Moderate')
        self.client.force_login(self.user)
        response = self.client.get(self.list_url, follow=True)
        assert response.status_code == 200
        doc = pq(response.content)
        assert doc('#result_list tbody tr').length == 4

        # Test truncated text while we're at it...
        content = response.content.decode('utf-8')
        assert (
            'Lôrem ipsum dolor sit amet, per at melius fuisset invidunt, ea '
            'facete aperiam his. Et cum iusto detracto, nam atqui nostrum no,'
            ' eum altera...' in content
        )
        # ... And add-on name display.
        assert str(self.addon.name) in content

        response = self.client.get(self.list_url, {'type': 'rating'}, follow=True)
        assert response.status_code == 200
        doc = pq(response.content)
        assert doc('#result_list tbody tr').length == 3

        response = self.client.get(self.list_url, {'type': 'reply'}, follow=True)
        assert response.status_code == 200
        doc = pq(response.content)
        assert doc('#result_list tbody tr').length == 1

    def test_filter_by_created(self):
        some_time_ago = self.days_ago(97).date()
        even_more_time_ago = self.days_ago(99).date()
        Rating.objects.create(
            addon=self.addon,
            body='Öld',
            rating=5,
            user=user_factory(),
            created=self.days_ago(98),
        )
        Rating.objects.create(
            addon=self.addon,
            body='Evên older',
            rating=5,
            user=user_factory(),
            created=self.days_ago(100),
        )
        data = {
            'created__range__gte': even_more_time_ago.isoformat(),
            'created__range__lte': some_time_ago.isoformat(),
        }
        self.grant_permission(self.user, 'Ratings:Moderate')
        self.client.force_login(self.user)
        response = self.client.get(self.list_url, data, follow=True)
        assert response.status_code == 200
        doc = pq(response.content.decode('utf-8'))
        assert doc('#result_list tbody tr').length == 1
        result_list_text = doc('#result_list tbody tr').text()
        assert 'Bär' not in result_list_text
        assert 'Evên older' not in result_list_text
        assert 'Öld' in result_list_text

        # Created filter should be selected. The rest shouldn't.
        lis = doc('#changelist-filter li.selected')
        # We've got 4 filters, so usually we'd get 4 selected list items
        # (because of the "All" default choice) but since 'created' is actually
        # 2 fields, and we have submitted both, we now have 5 expected items.
        assert len(lis) == 5
        assert lis.text().split() == ['All', 'All', 'All', 'From:', 'To:']
        elm = lis.eq(3).find('#id_created__range__gte')
        assert elm
        assert elm.attr('name') == 'created__range__gte'
        assert elm.attr('value') == even_more_time_ago.isoformat()
        elm = lis.eq(4).find('#id_created__range__lte')
        assert elm
        assert elm.attr('name') == 'created__range__lte'
        assert elm.attr('value') == some_time_ago.isoformat()

    def test_filter_by_created_only_from(self):
        not_long_ago = self.days_ago(2).date()
        Rating.objects.create(
            addon=self.addon,
            body='Öld',
            rating=5,
            user=user_factory(),
            created=self.days_ago(98),
        )
        Rating.objects.create(
            addon=self.addon,
            body='Evên older',
            rating=5,
            user=user_factory(),
            created=self.days_ago(100),
        )
        data = {
            'created__range__gte': not_long_ago.isoformat(),
        }
        self.grant_permission(self.user, 'Ratings:Moderate')
        self.client.force_login(self.user)
        response = self.client.get(self.list_url, data, follow=True)
        assert response.status_code == 200
        doc = pq(response.content.decode('utf-8'))
        assert doc('#result_list tbody tr').length == 1
        result_list_text = doc('#result_list tbody tr').text()
        assert 'Bär' in result_list_text
        assert 'Evên older' not in result_list_text
        assert 'Öld' not in result_list_text

        # Created filter should be selected. The rest shouldn't.
        lis = doc('#changelist-filter li.selected')
        # We should have 4 filters.
        assert len(lis) == 4
        assert lis.text().split() == ['All', 'All', 'All', 'From:']
        elm = lis.eq(3).find('#id_created__range__gte')
        assert elm
        assert elm.attr('name') == 'created__range__gte'
        assert elm.attr('value') == not_long_ago.isoformat()

    def test_filter_by_created_only_to(self):
        some_time_ago = self.days_ago(97).date()
        Rating.objects.create(
            addon=self.addon,
            body='Öld',
            rating=5,
            user=user_factory(),
            created=self.days_ago(98),
        )
        Rating.objects.create(
            addon=self.addon,
            body='Evên older',
            rating=5,
            user=user_factory(),
            created=self.days_ago(100),
        )
        data = {
            'created__range__lte': some_time_ago.isoformat(),
        }
        self.grant_permission(self.user, 'Ratings:Moderate')
        self.client.force_login(self.user)
        response = self.client.get(self.list_url, data, follow=True)
        assert response.status_code == 200
        doc = pq(response.content.decode('utf-8'))
        assert doc('#result_list tbody tr').length == 2
        result_list_text = doc('#result_list tbody tr').text()
        assert 'Bär' not in result_list_text
        assert 'Öld' in result_list_text
        assert 'Evên older' in result_list_text

        # Created filter should be selected. The rest shouldn't.
        lis = doc('#changelist-filter li.selected')
        # We should have 4 filters.
        assert len(lis) == 4
        assert lis.text().split() == ['All', 'All', 'All', 'To:']
        elm = lis.eq(3).find('#id_created__range__lte')
        assert elm
        assert elm.attr('name') == 'created__range__lte'
        assert elm.attr('value') == some_time_ago.isoformat()

    def test_queries(self):
        addon = Addon.objects.get(pk=3615)

        # Create a few more ratings.
        Rating.objects.create(
            addon=addon,
            user=user_factory(),
            rating=4,
            body='Lôrem ipsum dolor sit amet, per at melius fuisset '
            'invidunt, ea facete aperiam his. Et cum iusto detracto, '
            'nam atqui nostrum no, eum altera indoctum ad. Has ut duis '
            'tractatos laboramus, cum sale primis ei. Ius inimicus '
            'intellegebat ea, mollis expetendis usu ei. Cetero aeterno '
            'nostrud eu për.',
        )
        Rating.objects.create(addon=addon, body=None, rating=5, user=user_factory())
        # Create a reply.
        Rating.objects.create(
            addon=addon, user=self.user, body='Réply', reply_to=self.rating
        )

        self.grant_permission(self.user, 'Ratings:Moderate')
        self.client.force_login(self.user)
        with self.assertNumQueries(9):
            # - 2 Savepoint/release
            # - 2 user and its groups
            # - 1 COUNT(*)
            #     (show_full_result_count=False so we avoid the duplicate)
            # - 1 ratings themselves
            # - 1 related add-ons
            # - 1 related add-ons translations
            response = self.client.get(self.list_url, follow=True)
        assert response.status_code == 200
        doc = pq(response.content)
        assert doc('#result_list tbody tr').length == 4

    def test_can_not_access_detail_without_ratings_moderate_permission(self):
        user = user_factory(email='someone@mozilla.com')
        self.grant_permission(user, 'Addons:Edit')
        self.client.force_login(user)
        response = self.client.get(self.detail_url, follow=True)
        assert response.status_code == 403

    def test_can_not_delete_without_admin_advanced_permission(self):
        assert Rating.objects.count() == 1
        user = user_factory(email='someone@mozilla.com')
        self.grant_permission(user, 'Ratings:Moderate')  # Not enough!
        self.client.force_login(user)
        response = self.client.get(self.delete_url, follow=True)
        assert response.status_code == 403
        response = self.client.post(self.delete_url, {'post': 'yes'}, follow=True)
        assert response.status_code == 403

        assert Rating.objects.count() == 1
        assert Rating.unfiltered.count() == 1

    def test_can_delete_with_admin_advanced_permission(self):
        assert Rating.objects.count() == 1
        user = user_factory(email='someone@mozilla.com')
        self.grant_permission(user, 'Admin:Advanced')
        self.grant_permission(user, 'Ratings:Moderate')
        self.client.force_login(user)

        response = self.client.get(self.list_url, follow=True)
        assert response.status_code == 200
        assert b'Delete selected rating' in response.content

        response = self.client.get(self.delete_url, follow=True)
        assert response.status_code == 200
        assert b'Cannot delete rating' not in response.content
        response = self.client.post(self.delete_url, {'post': 'yes'}, follow=True)
        assert response.status_code == 200

        assert Rating.objects.count() == 0
        assert Rating.unfiltered.count() == 1

    def test_detail(self):
        user = UserProfile.objects.get(pk=999)
        self.grant_permission(user, 'Admin:Advanced')
        self.grant_permission(user, 'Ratings:Moderate')
        self.client.force_login(user)

        response = self.client.get(self.detail_url, follow=True)
        assert response.status_code == 200
