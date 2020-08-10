# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from unittest import mock

import os
import responses

from olympia.amo.storage_utils import copy_stored_file
from olympia.amo.tests import TestCase, addon_factory, reverse_ns, user_factory
from olympia.amo.tests.test_helpers import get_uploaded_file
from olympia.amo.urlresolvers import django_reverse, reverse
from django.conf import settings
from django.core.files.images import get_image_dimensions

from olympia.discovery.models import DiscoveryItem
from olympia.hero.models import (
    PrimaryHeroImage, SecondaryHero, SecondaryHeroModule)
from olympia.shelves.models import Shelf, ShelfManagement


class TestDiscoveryAdmin(TestCase):
    def setUp(self):
        self.list_url = reverse('admin:discovery_discoveryitem_changelist')

    def test_can_see_discovery_module_in_admin_with_discovery_edit(self):
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        url = reverse('admin:index')
        response = self.client.get(url)
        assert response.status_code == 200

        # Use django's reverse, since that's what the admin will use. Using our
        # own would fail the assertion because of the locale that gets added.
        self.list_url = django_reverse(
            'admin:discovery_discoveryitem_changelist')
        assert self.list_url in response.content.decode('utf-8')

    def test_can_list_with_discovery_edit_permission(self):
        DiscoveryItem.objects.create(addon=addon_factory(name=u'FooBâr'))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.list_url, follow=True)
        assert response.status_code == 200
        assert u'FooBâr' in response.content.decode('utf-8')

    def test_list_filtering_position_yes(self):
        DiscoveryItem.objects.create(
            addon=addon_factory(name=u'FooBâr'), position=1)
        DiscoveryItem.objects.create(addon=addon_factory(name=u'Âbsent'))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(
            self.list_url + '?position=yes', follow=True)
        assert response.status_code == 200
        assert u'FooBâr' in response.content.decode('utf-8')
        assert u'Âbsent' not in response.content.decode('utf-8')

    def test_list_filtering_position_no(self):
        DiscoveryItem.objects.create(
            addon=addon_factory(name=u'FooBâr'), position_china=42)
        DiscoveryItem.objects.create(
            addon=addon_factory(name=u'Âbsent'), position=1)
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.list_url + '?position=no', follow=True)
        assert response.status_code == 200
        assert u'FooBâr' in response.content.decode('utf-8')
        assert u'Âbsent' not in response.content.decode('utf-8')

    def test_list_filtering_position_yes_china(self):
        DiscoveryItem.objects.create(
            addon=addon_factory(name=u'FooBâr'), position_china=1)
        DiscoveryItem.objects.create(addon=addon_factory(name=u'Âbsent'))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(
            self.list_url + '?position_china=yes', follow=True)
        assert response.status_code == 200
        assert u'FooBâr' in response.content.decode('utf-8')
        assert u'Âbsent' not in response.content.decode('utf-8')

    def test_list_filtering_position_no_china(self):
        DiscoveryItem.objects.create(
            addon=addon_factory(name=u'FooBâr'), position=42)
        DiscoveryItem.objects.create(
            addon=addon_factory(name=u'Âbsent'), position_china=1)
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(
            self.list_url + '?position_china=no', follow=True)
        assert response.status_code == 200
        assert u'FooBâr' in response.content.decode('utf-8')
        assert u'Âbsent' not in response.content.decode('utf-8')

    def test_can_edit_with_discovery_edit_permission(self):
        addon = addon_factory(name=u'BarFöo')
        item = DiscoveryItem.objects.create(addon=addon)
        self.detail_url = reverse(
            'admin:discovery_discoveryitem_change', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.detail_url, follow=True)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert u'BarFöo' in content
        assert DiscoveryItem._meta.get_field('addon').help_text in content

        response = self.client.post(
            self.detail_url,
            {
                'addon': str(addon.pk),
                'custom_addon_name': u'Xäxâxàxaxaxa !',
                'custom_heading': u'This heading is totally custom.',
                'custom_description': u'This description is as well!',
            },
            follow=True)
        assert response.status_code == 200
        item.reload()
        assert DiscoveryItem.objects.count() == 1
        assert item.addon == addon
        assert item.custom_addon_name == u'Xäxâxàxaxaxa !'
        assert item.custom_heading == u'This heading is totally custom.'
        assert item.custom_description == u'This description is as well!'

    def test_translations_interpolation(self):
        addon = addon_factory(
            name='{bar}', users=[user_factory(display_name='{foo}')]
        )
        item = DiscoveryItem.objects.create(addon=addon)
        self.detail_url = reverse(
            'admin:discovery_discoveryitem_change', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.detail_url, follow=True)
        assert response.status_code == 200
        doc = pq(response.content)
        previews_content = doc('.field-previews').text()
        assert '{bar}' in previews_content
        assert '{foo}' in previews_content

        item.update(custom_addon_name='{abc}')
        self.client.login(email=user.email)
        response = self.client.get(self.detail_url, follow=True)
        assert response.status_code == 200
        doc = pq(response.content)
        previews_content = doc('.field-previews').text()
        assert '{bar}' in previews_content  # in description
        assert '{foo}' in previews_content  # in heading
        assert '{abc}' in previews_content  # in heading

        item.update(custom_heading='{def}', custom_description='{ghi}')
        self.client.login(email=user.email)
        response = self.client.get(self.detail_url, follow=True)
        assert response.status_code == 200
        doc = pq(response.content)
        previews_content = doc('.field-previews').text()
        assert '{bar}' not in previews_content  # overridden
        assert '{foo}' not in previews_content  # overridden
        assert '{abc}' not in previews_content  # overridden
        assert '{def}' in previews_content
        assert '{ghi}' in previews_content

    def test_can_change_addon_with_discovery_edit_permission(self):
        addon = addon_factory(name=u'BarFöo')
        addon2 = addon_factory(name=u'Another ône', slug='another-addon')
        item = DiscoveryItem.objects.create(addon=addon)
        self.detail_url = reverse(
            'admin:discovery_discoveryitem_change', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.detail_url, follow=True)
        assert response.status_code == 200
        assert u'BarFöo' in response.content.decode('utf-8')

        # Change add-on using the slug.
        response = self.client.post(
            self.detail_url,
            {'addon': str(addon2.slug)},
            follow=True)
        assert response.status_code == 200
        item.reload()
        assert DiscoveryItem.objects.count() == 1
        # assert item.addon == addon2

        # Change add-on using the id.
        response = self.client.post(
            self.detail_url,
            {'addon': str(addon.pk)},
            follow=True)
        assert response.status_code == 200
        item.reload()
        assert DiscoveryItem.objects.count() == 1
        assert item.addon == addon

    def test_change_addon_errors(self):
        addon = addon_factory(name=u'BarFöo')
        addon2 = addon_factory(name=u'Another ône', slug='another-addon')
        item = DiscoveryItem.objects.create(addon=addon)
        self.detail_url = reverse(
            'admin:discovery_discoveryitem_change', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)

        # Try changing using an unknown slug.
        response = self.client.post(
            self.detail_url,
            {'addon': u'gârbage'},
            follow=True)
        assert response.status_code == 200
        assert not response.context_data['adminform'].form.is_valid()
        assert 'addon' in response.context_data['adminform'].form.errors
        item.reload()
        assert item.addon == addon

        # Try changing using an unknown id.
        response = self.client.post(
            self.detail_url,
            {'addon': str(addon2.pk + 666)},
            follow=True)
        assert response.status_code == 200
        assert not response.context_data['adminform'].form.is_valid()
        assert 'addon' in response.context_data['adminform'].form.errors
        item.reload()
        assert item.addon == addon

        # Try changing to an add-on that is already used by another item.
        item2 = DiscoveryItem.objects.create(addon=addon2)
        response = self.client.post(
            self.detail_url,
            {'addon': str(addon2.pk)},
            follow=True)
        assert response.status_code == 200
        assert not response.context_data['adminform'].form.is_valid()
        assert 'addon' in response.context_data['adminform'].form.errors
        item.reload()
        item2.reload()
        assert item.addon == addon
        assert item2.addon == addon2

    def test_can_delete_with_discovery_edit_permission(self):
        item = DiscoveryItem.objects.create(addon=addon_factory())
        self.delete_url = reverse(
            'admin:discovery_discoveryitem_delete', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        # Can access delete confirmation page.
        response = self.client.get(self.delete_url, follow=True)
        assert response.status_code == 200
        assert DiscoveryItem.objects.filter(pk=item.pk).exists()

        # Can actually delete.
        response = self.client.post(
            self.delete_url,
            {'post': 'yes'},
            follow=True)
        assert response.status_code == 200
        assert not DiscoveryItem.objects.filter(pk=item.pk).exists()

    def test_can_add_with_discovery_edit_permission(self):
        addon = addon_factory(name=u'BarFöo')
        self.add_url = reverse('admin:discovery_discoveryitem_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.add_url, follow=True)
        assert response.status_code == 200
        assert DiscoveryItem.objects.count() == 0
        response = self.client.post(
            self.add_url,
            {
                'addon': str(addon.pk),
                'custom_addon_name': u'Xäxâxàxaxaxa !',
                'custom_heading': u'This heading is totally custom.',
                'custom_description': u'This description is as well!',
            },
            follow=True)
        assert response.status_code == 200
        assert DiscoveryItem.objects.count() == 1
        item = DiscoveryItem.objects.get()
        assert item.addon == addon
        assert item.custom_addon_name == u'Xäxâxàxaxaxa !'
        assert item.custom_heading == u'This heading is totally custom.'
        assert item.custom_description == u'This description is as well!'

    def test_can_not_add_without_discovery_edit_permission(self):
        addon = addon_factory(name=u'BarFöo')
        self.add_url = reverse('admin:discovery_discoveryitem_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(self.add_url, follow=True)
        assert response.status_code == 403
        response = self.client.post(
            self.add_url,
            {'addon': str(addon.pk)},
            follow=True)
        assert response.status_code == 403
        assert DiscoveryItem.objects.count() == 0

    def test_can_not_edit_without_discovery_edit_permission(self):
        addon = addon_factory(name=u'BarFöo')
        item = DiscoveryItem.objects.create(addon=addon)
        self.detail_url = reverse(
            'admin:discovery_discoveryitem_change', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(self.detail_url, follow=True)
        assert response.status_code == 403

        response = self.client.post(
            self.detail_url, {
                'addon': str(addon.pk),
                'custom_addon_name': u'Noooooô !',
                'custom_heading': u'I should not be able to do this.',
                'custom_description': u'This is wrong.',
            }, follow=True)
        assert response.status_code == 403
        item.reload()
        assert DiscoveryItem.objects.count() == 1
        assert item.addon == addon
        assert item.custom_addon_name == u''
        assert item.custom_heading == u''
        assert item.custom_description == u''

    def test_can_not_delete_without_discovery_edit_permission(self):
        item = DiscoveryItem.objects.create(addon=addon_factory())
        self.delete_url = reverse(
            'admin:discovery_discoveryitem_delete', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        # Can not access delete confirmation page.
        response = self.client.get(self.delete_url, follow=True)
        assert response.status_code == 403
        assert DiscoveryItem.objects.filter(pk=item.pk).exists()

        # Can not actually delete either.
        response = self.client.post(
            self.delete_url, data={'post': 'yes'}, follow=True)
        assert response.status_code == 403
        assert DiscoveryItem.objects.filter(pk=item.pk).exists()

    def test_query_count(self):
        DiscoveryItem.objects.create(addon=addon_factory(name=u'FooBâr'))
        DiscoveryItem.objects.create(addon=addon_factory(name=u'FooBâr 2'))
        DiscoveryItem.objects.create(addon=addon_factory(name=u'FooBâr 3'))
        DiscoveryItem.objects.create(addon=addon_factory(name=u'FooBâr 4'))
        DiscoveryItem.objects.create(addon=addon_factory(name=u'FooBâr 5'))
        DiscoveryItem.objects.create(addon=addon_factory(name=u'FooBâr 6'))

        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)

        # 1. select current user
        # 2. savepoint (because we're in tests)
        # 3. select groups
        # 4. pagination count
        # 5. pagination count (double…)
        # 6. select list of discovery items, ordered
        # 7. prefetch add-ons
        # 8. select translations for add-ons from 7.
        # 9. savepoint (because we're in tests)
        with self.assertNumQueries(9):
            response = self.client.get(self.list_url, follow=True)

        DiscoveryItem.objects.create(addon=addon_factory(name=u'FooBâr 5'))
        DiscoveryItem.objects.create(addon=addon_factory(name=u'FooBâr 6'))

        # Ensure the count is stable
        with self.assertNumQueries(9):
            response = self.client.get(self.list_url, follow=True)

        assert response.status_code == 200


class TestPrimaryHeroImageAdmin(TestCase):
    def setUp(self):
        self.list_url = reverse(
            'admin:discovery_primaryheroimageupload_changelist')
        self.detail_url_name = 'admin:discovery_primaryheroimageupload_change'

    def test_can_see_primary_hero_image_in_admin_with_discovery_edit(self):
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        url = reverse('admin:index')
        response = self.client.get(url)
        assert response.status_code == 200

        # Use django's reverse, since that's what the admin will use. Using our
        # own would fail the assertion because of the locale that gets added.
        self.list_url = django_reverse(
            'admin:discovery_primaryheroimageupload_changelist')
        assert self.list_url in response.content.decode('utf-8')

    def test_can_list_with_discovery_edit_permission(self):
        uploaded_photo = get_uploaded_file('transparent.png')
        PrimaryHeroImage.objects.create(custom_image=uploaded_photo)
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.list_url, follow=True)
        assert response.status_code == 200
        assert 'transparent.jpg' in response.content.decode('utf-8')

    def test_can_edit_with_discovery_edit_permission(self):
        uploaded_photo = get_uploaded_file('transparent.png')
        item = PrimaryHeroImage.objects.create(custom_image=uploaded_photo)
        self.detail_url = reverse(
            'admin:discovery_primaryheroimageupload_change', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.detail_url, follow=True)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert u'transparent.jpg' in content

        updated_photo = get_uploaded_file('preview_4x3.jpg')
        response = self.client.post(
            self.detail_url,
            dict(custom_image=updated_photo),
            follow=True)
        assert response.status_code == 200
        item.reload()
        assert PrimaryHeroImage.objects.count() == 1
        assert item.custom_image == 'hero-featured-image/preview_4x3.jpg'
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'preview_4x3.jpg'))
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image',
            'thumbs', 'preview_4x3.jpg'))
        width, height = get_image_dimensions(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'preview_4x3.jpg'))
        t_width, t_height = get_image_dimensions(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image',
            'thumbs', 'preview_4x3.jpg'))
        assert width <= 960 and height <= 640
        assert t_width <= 150 and t_height <= 120

    def test_can_delete_with_discovery_edit_permission(self):
        uploaded_photo = get_uploaded_file('transparent.png')
        item = PrimaryHeroImage.objects.create(custom_image=uploaded_photo)
        src = os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'transparent.jpg')
        dest = os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'thumbs',
            'transparent.jpg')
        copy_stored_file(src, dest)
        delete_url = reverse(
            'admin:discovery_primaryheroimageupload_delete', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        # Can access delete confirmation page.
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 200
        assert PrimaryHeroImage.objects.filter(pk=item.pk).exists()
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'transparent.jpg'))
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'thumbs',
            'transparent.jpg'))

        # And can actually delete.
        response = self.client.post(
            delete_url, data={'post': 'yes'}, follow=True)
        assert response.status_code == 200
        assert not PrimaryHeroImage.objects.filter(pk=item.pk).exists()
        assert not os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'transparent.jpg'))
        assert not os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image',
            'thumbs', 'transparent.jpg'))

    def test_can_add_with_discovery_edit_permission(self):
        add_url = reverse('admin:discovery_primaryheroimageupload_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(add_url, follow=True)
        assert response.status_code == 200
        assert PrimaryHeroImage.objects.count() == 0
        photo = get_uploaded_file('transparent.png')
        response = self.client.post(
            add_url,
            dict(custom_image=photo),
            follow=True)
        assert response.status_code == 200
        assert PrimaryHeroImage.objects.count() == 1
        item = PrimaryHeroImage.objects.get()
        assert item.custom_image == 'hero-featured-image/transparent.jpg'
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'transparent.jpg'))
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image',
            'thumbs', 'transparent.jpg'))
        width, height = get_image_dimensions(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'transparent.jpg'))
        t_width, t_height = get_image_dimensions(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image',
            'thumbs', 'transparent.jpg'))
        assert width <= 960 and height <= 640
        assert t_width <= 150 and t_height <= 120

    def test_can_not_add_without_discovery_edit_permission(self):
        add_url = reverse('admin:discovery_primaryheroimageupload_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(add_url, follow=True)
        assert response.status_code == 403
        photo = get_uploaded_file('transparent.png')
        response = self.client.post(
            add_url,
            dict(custom_image=photo),
            follow=True)
        assert response.status_code == 403
        assert PrimaryHeroImage.objects.count() == 0

    def test_can_not_edit_without_discovery_edit_permission(self):
        uploaded_photo = get_uploaded_file('transparent.png')
        item = PrimaryHeroImage.objects.create(custom_image=uploaded_photo)
        detail_url = reverse(
            'admin:discovery_primaryheroimageupload_change', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(detail_url, follow=True)
        assert response.status_code == 403
        updated_photo = get_uploaded_file('non-animated.png')

        response = self.client.post(
            detail_url,
            dict(custom_image=updated_photo),
            follow=True)
        assert response.status_code == 403
        item.reload()
        assert PrimaryHeroImage.objects.count() == 1
        assert item.custom_image == 'hero-featured-image/transparent.jpg'

    def test_can_not_delete_without_discovery_edit_permission(self):
        uploaded_photo = get_uploaded_file('transparent.png')
        item = PrimaryHeroImage.objects.create(custom_image=uploaded_photo)
        src = os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'transparent.jpg')
        dest = os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'thumbs',
            'transparent.jpg')
        copy_stored_file(src, dest)
        delete_url = reverse(
            'admin:discovery_primaryheroimageupload_delete', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        # Can not access delete confirmation page.
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 403
        assert PrimaryHeroImage.objects.filter(pk=item.pk).exists()
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'transparent.jpg'))
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'thumbs',
            'transparent.jpg'))

        # Can not actually delete either.
        response = self.client.post(
            delete_url, data={'post': 'yes'}, follow=True)
        assert response.status_code == 403
        assert PrimaryHeroImage.objects.filter(pk=item.pk).exists()
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image', 'transparent.jpg'))
        assert os.path.exists(os.path.join(
            settings.MEDIA_ROOT, 'hero-featured-image',
            'thumbs', 'transparent.jpg'))


class TestSecondaryHeroShelfAdmin(TestCase):
    def setUp(self):
        self.list_url = reverse(
            'admin:discovery_secondaryheroshelf_changelist')
        self.detail_url_name = 'admin:discovery_secondaryheroshelf_change'

    def _get_moduleform(self, item, module_data, initial=0):
        count = str(len(module_data))
        out = {
            "modules-TOTAL_FORMS": count,
            "modules-INITIAL_FORMS": initial,
            "modules-MIN_NUM_FORMS": count,
            "modules-MAX_NUM_FORMS": count,
            "modules-__prefix__-icon": "",
            "modules-__prefix__-description": "",
            "modules-__prefix__-id": "",
            "modules-__prefix__-shelf": str(item),
        }
        for index in range(0, len(module_data)):
            out.update(**{
                f"modules-{index}-icon": str(module_data[index]['icon']),
                f"modules-{index}-description": str(
                    module_data[index]['description']),
                f"modules-{index}-id": str(module_data[index].get('id', '')),
                f"modules-{index}-shelf": str(item),

            })
        return out

    def test_can_see_secondary_hero_module_in_admin_with_discovery_edit(self):
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        url = reverse('admin:index')
        response = self.client.get(url)
        assert response.status_code == 200

        # Use django's reverse, since that's what the admin will use. Using our
        # own would fail the assertion because of the locale that gets added.
        self.list_url = django_reverse(
            'admin:discovery_secondaryheroshelf_changelist')
        assert self.list_url in response.content.decode('utf-8')

    def test_can_list_with_discovery_edit_permission(self):
        SecondaryHero.objects.create(headline='FooBâr')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.list_url, follow=True)
        assert response.status_code == 200
        assert 'FooBâr' in response.content.decode('utf-8')

    def test_can_edit_with_discovery_edit_permission(self):
        item = SecondaryHero.objects.create(headline='BarFöo')
        modules = [
            SecondaryHeroModule.objects.create(shelf=item),
            SecondaryHeroModule.objects.create(shelf=item),
            SecondaryHeroModule.objects.create(shelf=item),
        ]
        detail_url = reverse(self.detail_url_name, args=(item.pk,))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(detail_url, follow=True)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'BarFöo' in content
        assert 'Not selected' in content

        shelves = [
            {
                'id': modules[0].id,
                'description': 'foo',
                'icon': 'Audio.svg'
            },
            {
                'id': modules[1].id,
                'description': 'baa',
                'icon': 'Developer.svg',
            },
            {
                'id': modules[2].id,
                'description': 'ugh',
                'icon': 'Extensions.svg',
            },
        ]
        response = self.client.post(
            detail_url,
            dict(self._get_moduleform(item.id, shelves, initial=3), **{
                'headline': 'This headline is ... something.',
                'description': 'This description is as well!',
            }), follow=True)
        assert response.status_code == 200
        assert 'errors' not in response.context_data, (
            response.context_data['errors'])
        item.reload()
        assert SecondaryHero.objects.count() == 1
        assert item.headline == 'This headline is ... something.'
        assert item.description == 'This description is as well!'
        assert SecondaryHeroModule.objects.count() == 3
        (module.reload() for module in modules)
        module_values = list(
            SecondaryHeroModule.objects.all().values(
                'id', 'description', 'icon'))
        assert module_values == shelves

    def test_can_delete_with_discovery_edit_permission(self):
        item = SecondaryHero.objects.create()
        delete_url = reverse(
            'admin:discovery_secondaryheroshelf_delete', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        # Can access delete confirmation page.
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 200
        assert SecondaryHero.objects.filter(pk=item.pk).exists()

        # But not if the shelf is the only enabled shelf
        item.update(enabled=True)
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 403

        # We can't actually delete either.
        response = self.client.post(
            delete_url,
            dict(self._get_moduleform(item.pk, {}), post='yes'),
            follow=True)
        assert response.status_code == 403
        assert SecondaryHero.objects.filter(pk=item.pk).exists()

        # Add another enabled shelf and we should be okay to delete again
        SecondaryHero.objects.create(enabled=True)
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 200

        # And can actually delete.
        response = self.client.post(
            delete_url,
            dict(self._get_moduleform(item.pk, {}), post='yes'),
            follow=True)
        assert response.status_code == 200
        assert not SecondaryHero.objects.filter(pk=item.pk).exists()
        assert not SecondaryHeroModule.objects.filter(shelf=item.pk).exists()

    def test_can_add_with_discovery_edit_permission(self):
        add_url = reverse('admin:discovery_secondaryheroshelf_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(add_url, follow=True)
        assert response.status_code == 200
        assert SecondaryHero.objects.count() == 0
        assert SecondaryHeroModule.objects.count() == 0
        shelves = [
            {
                'description': 'foo',
                'icon': 'Audio.svg'
            },
            {
                'description': 'baa',
                'icon': 'Developer.svg',
            },
            {
                'description': 'ugh',
                'icon': 'Extensions.svg',
            },
        ]
        response = self.client.post(
            add_url,
            dict(self._get_moduleform('', shelves), **{
                'headline': 'This headline is ... something.',
                'description': 'This description is as well!',
            }),
            follow=True)
        assert response.status_code == 200
        assert 'errors' not in response.context_data
        assert SecondaryHero.objects.count() == 1
        item = SecondaryHero.objects.get()
        assert item.headline == 'This headline is ... something.'
        assert item.description == 'This description is as well!'
        assert SecondaryHeroModule.objects.count() == 3
        module_values = list(
            SecondaryHeroModule.objects.all().values('description', 'icon'))
        assert module_values == shelves

    def test_can_not_add_without_discovery_edit_permission(self):
        add_url = reverse('admin:discovery_secondaryheroshelf_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(add_url, follow=True)
        assert response.status_code == 403
        response = self.client.post(
            add_url, {
                'headline': 'This headline is ... something.',
                'description': 'This description is as well!',
            },
            follow=True)
        assert response.status_code == 403
        assert SecondaryHero.objects.count() == 0

    def test_can_not_edit_without_discovery_edit_permission(self):
        item = SecondaryHero.objects.create()
        detail_url = reverse(
            'admin:discovery_secondaryheroshelf_change', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(detail_url, follow=True)
        assert response.status_code == 403

        response = self.client.post(
            detail_url, {
                'headline': 'I should not be able to do this.',
                'description': 'This is wrong.',
            }, follow=True)
        assert response.status_code == 403
        item.reload()
        assert SecondaryHero.objects.count() == 1
        assert item.headline == ''
        assert item.description == ''

    def test_can_not_delete_without_discovery_edit_permission(self):
        item = SecondaryHero.objects.create()
        delete_url = reverse(
            'admin:discovery_secondaryheroshelf_delete', args=(item.pk,)
        )
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        # Can not access delete confirmation page.
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 403
        assert SecondaryHero.objects.filter(pk=item.pk).exists()

        # Can not actually delete either.
        response = self.client.post(
            delete_url, data={'post': 'yes'}, follow=True)
        assert response.status_code == 403
        assert SecondaryHero.objects.filter(pk=item.pk).exists()

    def test_need_3_modules(self):
        add_url = reverse('admin:discovery_secondaryheroshelf_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(add_url, follow=True)
        assert response.status_code == 200
        assert SecondaryHero.objects.count() == 0
        response = self.client.post(
            add_url,
            dict(self._get_moduleform('', {}), **{
                'headline': 'This headline is ... something.',
                'description': 'This description is as well!',
            }),
            follow=True)
        assert response.status_code == 200
        assert 'There must be exactly 3 modules in this shelf.' in (
            response.context_data['errors'])
        assert SecondaryHero.objects.count() == 0


class TestShelfAdmin(TestCase):
    def setUp(self):
        self.list_url = reverse(
            'admin:discovery_shelfmodule_changelist')
        self.detail_url_name = 'admin:discovery_shelfmodule_change'

        criteria_sea = '?recommended=true&sort=random&type=extension'
        responses.add(
            responses.GET,
            reverse_ns('addon-search') + criteria_sea,
            status=200,
            json={'count': 103})

    def test_can_see_shelf_module_in_admin_with_discovery_edit(self):
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        url = reverse('admin:index')
        response = self.client.get(url)
        assert response.status_code == 200

        # Use django's reverse, since that's what the admin will use. Using our
        # own would fail the assertion because of the locale that gets added.
        self.list_url = django_reverse(
            'admin:discovery_shelfmodule_changelist')
        assert self.list_url in response.content.decode('utf-8')

    def test_can_list_with_discovery_edit_permission(self):
        Shelf.objects.create(title='FooBâr')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.list_url, follow=True)
        assert response.status_code == 200
        assert 'FooBâr' in response.content.decode('utf-8')

    def test_can_edit_with_discovery_edit_permission(self):
        item = Shelf.objects.create(
            title='Popular extensions',
            endpoint='search',
            criteria='?sort=users&type=extension',
            footer_text='See more',
            footer_pathname='/this/is/the/pathname')
        detail_url = reverse(self.detail_url_name, args=(item.pk,))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(detail_url, follow=True)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'Popular extensions' in content

        with mock.patch('olympia.shelves.forms.ShelfForm.clean') as mock_clean:
            mock_clean.return_value = {
                'title': 'Recommended extensions',
                'endpoint': 'search',
                'criteria': (
                    '?recommended=true&sort=random&type=extension'),
                'footer_text': 'See more',
                'footer_pathname': '/this/is/the/pathname'
            }

            response = self.client.post(
                detail_url,
                mock_clean.return_value,
                follow=True)
            assert response.status_code == 200
            item.reload()
            assert Shelf.objects.count() == 1
            assert item.title == 'Recommended extensions'
            assert item.endpoint == 'search'
            assert item.criteria == (
                '?recommended=true&sort=random&type=extension')

    def test_can_delete_with_discovery_edit_permission(self):
        item = Shelf.objects.create(
            title='Recommended extensions',
            endpoint='search',
            criteria='?recommended=true&sort=random&type=extension',
            footer_text='See more',
            footer_pathname='/this/is/the/pathname')
        delete_url = reverse(
            'admin:discovery_shelfmodule_delete', args=(item.pk,))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        # Can access delete confirmation page.
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 200
        assert Shelf.objects.filter(pk=item.pk).exists()

        # And can actually delete.
        response = self.client.post(
            delete_url, data={'post': 'yes'}, follow=True)
        assert response.status_code == 200
        assert not Shelf.objects.filter(pk=item.pk).exists()

    def test_can_add_with_discovery_edit_permission(self):
        add_url = reverse('admin:discovery_shelfmodule_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(add_url, follow=True)
        assert response.status_code == 200
        assert Shelf.objects.count() == 0

        with mock.patch('olympia.shelves.forms.ShelfForm.clean') as mock_clean:
            mock_clean.return_value = {
                'title': 'Recommended extensions',
                'endpoint': 'search',
                'criteria':
                    ('?recommended=true&sort=random&type=extension'),
                'footer_text': 'See more',
                'footer_pathname': '/this/is/the/pathname',
            }

            response = self.client.post(
                add_url,
                mock_clean.return_value,
                follow=True)

            assert response.status_code == 200
            assert Shelf.objects.count() == 1
            item = Shelf.objects.get()
            assert item.title == 'Recommended extensions'
            assert item.endpoint == 'search'
            assert item.criteria == (
                '?recommended=true&sort=random&type=extension')

    def test_can_not_add_without_discovery_edit_permission(self):
        add_url = reverse('admin:discovery_shelfmodule_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(add_url, follow=True)
        assert response.status_code == 403
        response = self.client.post(
            add_url,
            {
                'title': 'Recommended extensions',
                'endpoint': 'search',
                'criteria':
                '?recommended=true&sort=random&type=extension',
                'footer_text': 'See more',
                'footer_pathname': '/this/is/the/pathname'
            },
            follow=True)
        assert response.status_code == 403
        assert Shelf.objects.count() == 0

    def test_can_not_edit_without_discovery_edit_permission(self):
        item = Shelf.objects.create(
            title='Recommended extensions',
            endpoint='search',
            criteria='?recommended=true&sort=random&type=extension',
            footer_text='See more',
            footer_pathname='/this/is/the/pathname')
        detail_url = reverse(
            'admin:discovery_shelfmodule_change', args=(item.pk,))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(detail_url, follow=True)
        assert response.status_code == 403

        response = self.client.post(
            detail_url,
            {
                'title': 'Popular extensions',
                'endpoint': 'search',
                'criteria':
                '?recommended=true&sort=users&type=extension',
                'footer_text': 'See more',
                'footer_pathname': '/this/is/the/pathname'
            }, follow=True)
        assert response.status_code == 403
        item.reload()
        assert Shelf.objects.count() == 1
        assert item.title == 'Recommended extensions'

    def test_can_not_delete_without_discovery_edit_permission(self):
        item = Shelf.objects.create(
            title='Recommended extensions',
            endpoint='search',
            criteria='?recommended=true&sort=random&type=extension',
            footer_text='See more',
            footer_pathname='/this/is/the/pathname')
        delete_url = reverse(
            'admin:discovery_shelfmodule_delete', args=(item.pk,))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        # Can not access delete confirmation page.
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 403
        assert Shelf.objects.filter(pk=item.pk).exists()

        # Can not actually delete either.
        response = self.client.post(
            delete_url, data={'post': 'yes'}, follow=True)
        assert response.status_code == 403
        assert Shelf.objects.filter(pk=item.pk).exists()
        assert item.title == 'Recommended extensions'


class TestHomepageShelvesAdmin(TestCase):
    def setUp(self):
        self.list_url = reverse(
            'admin:discovery_homepageshelves_changelist')
        self.detail_url_name = 'admin:discovery_homepageshelves_change'
        self.shelf = Shelf.objects.create(
            title='Populâr themes',
            endpoint='search',
            criteria='?sort=users&type=statictheme')

    def test_can_see_homepage_shelves_in_admin_with_discovery_edit(self):
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        url = reverse('admin:index')
        response = self.client.get(url)
        assert response.status_code == 200

        # Use django's reverse, since that's what the admin will use. Using our
        # own would fail the assertion because of the locale that gets added.
        self.list_url = django_reverse(
            'admin:discovery_homepageshelves_changelist')
        assert self.list_url in response.content.decode('utf-8')

    def test_can_list_with_discovery_edit_permission(self):
        ShelfManagement.objects.create(shelf=self.shelf)
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(self.list_url, follow=True)
        assert response.status_code == 200
        assert 'Populâr themes' in response.content.decode('utf-8')

    def test_can_edit_with_discovery_edit_permission(self):
        hpshelf = ShelfManagement.objects.create(shelf=self.shelf, position=1)
        detail_url = reverse(self.detail_url_name, args=(hpshelf.pk,))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(detail_url, follow=True)
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'Populâr themes' in content

        response = self.client.post(
            detail_url,
            {
                'shelf': self.shelf.pk,
                'position': 2
            }, follow=True)
        assert response.status_code == 200
        hpshelf.reload()
        assert ShelfManagement.objects.count() == 1
        assert hpshelf.shelf.title == 'Populâr themes'
        assert hpshelf.position == 2

    def test_can_delete_with_discovery_edit_permission(self):
        hpshelf = ShelfManagement.objects.create(shelf=self.shelf)
        delete_url = reverse(
            'admin:discovery_homepageshelves_delete', args=(hpshelf.pk,))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        # Can access delete confirmation page.
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 200
        assert ShelfManagement.objects.filter(pk=hpshelf.pk).exists()

        # And can actually delete.
        response = self.client.post(
            delete_url, data={'post': 'yes'}, follow=True)
        assert response.status_code == 200
        assert not ShelfManagement.objects.filter(pk=hpshelf.pk).exists()

    def test_can_add_with_discovery_edit_permission(self):
        add_url = reverse('admin:discovery_homepageshelves_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.grant_permission(user, 'Discovery:Edit')
        self.client.login(email=user.email)
        response = self.client.get(add_url, follow=True)
        assert response.status_code == 200
        assert ShelfManagement.objects.count() == 0
        response = self.client.post(
            add_url,
            {
                'shelf': self.shelf.pk,
                'position': 0,
            },
            follow=True)
        assert response.status_code == 200
        assert ShelfManagement.objects.count() == 1
        hpshelf = ShelfManagement.objects.get()
        assert hpshelf.shelf == self.shelf
        assert hpshelf.shelf.title == 'Populâr themes'

    def test_can_not_add_without_discovery_edit_permission(self):
        add_url = reverse('admin:discovery_homepageshelves_add')
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(add_url, follow=True)
        assert response.status_code == 403
        response = self.client.post(
            add_url,
            {'shelf': self.shelf.pk},
            follow=True)
        assert response.status_code == 403
        assert ShelfManagement.objects.count() == 0

    def test_can_not_edit_without_discovery_edit_permission(self):
        hpshelf = ShelfManagement.objects.create(shelf=self.shelf)
        detail_url = reverse(
            'admin:discovery_homepageshelves_change', args=(hpshelf.pk,))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        response = self.client.get(detail_url, follow=True)
        assert response.status_code == 403

        response = self.client.post(
            detail_url,
            {
                'position': 1,
                'shelf': self.shelf.pk
            }, follow=True)
        assert response.status_code == 403
        hpshelf.reload()
        assert ShelfManagement.objects.count() == 1
        assert hpshelf.position == 0

    def test_can_not_delete_without_discovery_edit_permission(self):
        hpshelf = ShelfManagement.objects.create(shelf=self.shelf)
        delete_url = reverse(
            'admin:discovery_homepageshelves_delete', args=(hpshelf.pk,))
        user = user_factory()
        self.grant_permission(user, 'Admin:Tools')
        self.client.login(email=user.email)
        # Can not access delete confirmation page.
        response = self.client.get(delete_url, follow=True)
        assert response.status_code == 403
        assert ShelfManagement.objects.filter(pk=hpshelf.pk).exists()

        # Can not actually delete either.
        response = self.client.post(
            delete_url, data={'post': 'yes'}, follow=True)
        assert response.status_code == 403
        assert ShelfManagement.objects.filter(pk=hpshelf.pk).exists()
        assert hpshelf.shelf.title == 'Populâr themes'
