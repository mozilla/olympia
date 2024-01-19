from django import forms
from django.utils.translation import gettext_lazy as _

from olympia.api.throttling import (
    CheckThrottlesFormMixin,
    GranularIPRateThrottle,
    GranularUserRateThrottle,
)


class HourlyAbuseAppealUserThrottle(GranularUserRateThrottle):
    rate = '6/hour'
    scope = 'hourly_user_abuse_appeal'


class HourlyAbuseAppealIPThrottle(GranularIPRateThrottle):
    rate = '6/hour'
    scope = 'hourly_ip_abuse_appeal'


class AbuseAppealUserThrottle(GranularUserRateThrottle):
    rate = '20/day'
    scope = 'daily_user_abuse_appeal'


class AbuseAppealIPThrottle(GranularIPRateThrottle):
    rate = '20/day'
    scope = 'daily_ip_abuse_appeal'


class AbuseAppealEmailForm(CheckThrottlesFormMixin, forms.Form):
    # Note: the label is generic on purpose. It could be an appeal from the
    # reporter, or from the target of a ban (who can no longer log in).
    email = forms.EmailField(label=_('Email address'))

    throttled_error_message = _(
        'You have submitted this form too many times recently. '
        'Please try again after some time.'
    )

    throttle_classes = (
        HourlyAbuseAppealIPThrottle,
        AbuseAppealIPThrottle,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.expected_email = kwargs.pop('expected_email')
        return super().__init__(*args, **kwargs)

    def clean_email(self):
        if (email := self.cleaned_data['email']) != self.expected_email:
            raise forms.ValidationError(_('Invalid email provided.'))
        return email


class AbuseAppealForm(CheckThrottlesFormMixin, forms.Form):
    error_message = _(
        'You have submitted this form too many times recently. '
        'Please try again after some time.'
    )

    throttle_classes = (
        HourlyAbuseAppealIPThrottle,
        AbuseAppealIPThrottle,
        HourlyAbuseAppealIPThrottle,
        AbuseAppealUserThrottle,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        return super().__init__(*args, **kwargs)

    reason = forms.CharField(
        widget=forms.Textarea(),
        label=_('Reason for appeal'),
        help_text=_(
            'Please explain why you believe that this decision was made in error, '
            'and/or does not align with the applicable policy or law.'
        ),
    )
