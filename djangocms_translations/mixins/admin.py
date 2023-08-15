import json

from django.conf.urls import url
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from djangocms_translations.admin import AllReadOnlyFieldsMixin
from djangocms_translations.utils import pretty_json

from . import models, views

__all__ = [
    'TranslateAppMixin',
    'AppTranslationRequestAdmin',
]

from .models import AppTranslationRequest


class AppTranslationRequestItemInline(AllReadOnlyFieldsMixin, admin.TabularInline):
    model = models.AppTranslationRequestItem
    extra = 0
    classes = ['collapse']


class AppTranslationQuoteInline(AllReadOnlyFieldsMixin, admin.TabularInline):
    model = models.AppTranslationQuote
    extra = 0
    classes = ['collapse']


class AppTranslationOrderInline(AllReadOnlyFieldsMixin, admin.StackedInline):
    model = models.AppTranslationOrder
    extra = 0
    classes = ['collapse']

    fields = (
        'provider_order_id',
        (
            'date_created',
            'date_translated',
        ),
        'state',
        'pretty_provider_options',
        'pretty_request_content',
        'pretty_response_content',
        'price',
    )

    readonly_fields = (
        'provider_order_id',
        'pretty_provider_options',
        'pretty_request_content',
        'pretty_response_content',
        'price',
    )

    def provider_order_id(self, obj):
        return obj.provider_details.get('Id') or obj.response_content.get('Id')

    provider_order_id.short_description = _('Provider order ID')

    def pretty_provider_options(self, obj):
        return pretty_json(json.dumps(obj.provider_options))

    pretty_provider_options.short_description = _('Provider options')

    def pretty_request_content(self, obj):
        return pretty_json(json.dumps(obj.request_content))

    pretty_request_content.short_description = _('Request content')

    def pretty_response_content(self, obj):
        if isinstance(obj.response_content, dict):
            data = json.dumps(obj.response_content)
        else:
            data = obj.response_content
        return pretty_json(data)

    pretty_response_content.short_description = _('Response content')

    def price(self, obj):
        return obj.price_with_currency

    price.short_description = _('Price')


@admin.register(AppTranslationRequest)
class AppTranslationRequestAdmin(AllReadOnlyFieldsMixin, admin.ModelAdmin):
    inlines = [
        AppTranslationQuoteInline,
        AppTranslationRequestItemInline,
        AppTranslationOrderInline,
    ]

    list_filter = ('state',)
    list_display = (
        'provider_order_name',
        'date_created',
        # 'pages_sent',
        # 'pretty_source_language',
        # 'pretty_target_language',
        'pretty_status',
    )

    fieldsets = (
        (None, {
            'fields': (
                'provider_order_name',
                'user',
                'state',
                (
                    'date_created',
                    'date_submitted',
                    'date_received',
                    'date_imported',
                ),
                (
                    # 'pretty_source_language',
                    # 'pretty_target_language',
                ),
                'provider_backend',
            ),
        }),
        (_('Additional info'), {
            'fields': (
                'pretty_provider_options',
                'pretty_export_content',
                # 'pretty_request_content',
                # 'selected_quote',
            ),
            'classes': ('collapse',),
        }),
    )

    #
    readonly_fields = (
        #     'provider_order_name',
        #     'date_created',
        #     'date_submitted',
        #     'date_received',
        #     'date_imported',
        #     'pretty_source_language',
        #     'pretty_target_language',
        'pretty_provider_options',
        'pretty_export_content',
        #     'pretty_request_content',
        #     'selected_quote',
    )

    def pretty_provider_options(self, obj):
        return pretty_json(json.dumps(obj.provider_options))

    pretty_provider_options.short_description = _('Provider options')

    def pretty_export_content(self, obj):
        if isinstance(obj.export_content, dict):
            data = json.dumps(obj.export_content)
        else:
            data = obj.export_content
        return pretty_json(data)

    pretty_export_content.short_description = _('Export content')

    def get_urls(self):
        return [
            url(
                r'add/$',
                views.CreateTranslationRequestView.as_view(),
                name='create-app-translation-request',
            ),
            url(
                r'(?P<pk>\w+)/get-quote-from-provider/$',
                views.get_quote_from_provider_view,
                name='get-quote-from-provider',
            ),
            url(
                r'(?P<pk>\w+)/choose-quote/$',
                views.ChooseTranslationQuoteView.as_view(),
                name='choose-app-translation-quote',
            ),
            url(
                r'(?P<pk>\w+)/callback/$',
                views.process_provider_callback_view,
                name='app-translation-request-provider-callback',
            ),
        ] + super(AppTranslationRequestAdmin, self).get_urls()

    def pretty_status(self, obj):
        action = ''

        def render_action(url, title):
            return mark_safe(
                '<a class="button" href="{url}">{title}</a>'
                .format(url=url, title=title)
            )

        if obj.state == models.AppTranslationRequest.STATES.PENDING_QUOTE:
            action = mark_safe(
                '<a class="button" '
                'onclick="window.django.jQuery.ajax({{'  # noqa
                'method: \'POST\', headers: {headers}, url: \'{url}\', success: {refresh_window_callback}'
                '}});" href="#">{title}</a>'.format(
                    url=reverse('admin:get-quote-from-provider', args=(obj.pk,)),
                    title=_('Refresh'),
                    headers='{\'X-CSRFToken\': document.cookie.match(/csrftoken=(\w+)(;|$)/)[1]}',
                    refresh_window_callback='function () {window.location.reload()}',
                )
            )
        elif obj.state == models.AppTranslationRequest.STATES.PENDING_APPROVAL:
            action = render_action(
                reverse('admin:choose-app-translation-quote', args=(obj.pk,)),
                _('Choose quote'),
            )
        # elif obj.state == models.AppTranslationRequest.STATES.IMPORT_FAILED:
        #     action = render_action(
        #         reverse('admin:translation-request-show-log', args=(obj.pk,)),
        #         _('Log'),
        #     )
        return format_html(
            '{status} {action}',
            status=obj.get_state_display(),
            action=action,
        )

    pretty_status.short_description = _('Status')


class TranslateAppMixin(object):
    """
    ModelAdmin mixin used to add translate content with gpt provider
    """
    action = ""

    def send_translation_request(self, obj):
        print("send_translation_request", obj._meta.app_label)

        def render_action(url, title):
            return mark_safe(
                '<a class="button" href="{url}">{title}</a>'
                .format(url=url, title=title)
            )

        action = render_action(
            (
                '{url}?link_model={link_model}&app_label={app_label}&link_object_id={app_id}&source_language={source_language}'
                .format(url=reverse('admin:create-app-translation-request'), app_label=obj._meta.app_label,
                        link_model=obj._meta.model_name, app_id=obj.pk,
                        source_language="de")),
            # TODO read language from request
            _('Translate app'),
        )

        print("action", obj.pk)

        return format_html(
            '{status} {action}',
            status="Translate",
            action=action,
        )

    send_translation_request.short_description = 'Translate'
    send_translation_request.allow_tags = True

    def get_list_display(self, request):
        list_display = super(TranslateAppMixin, self).get_list_display(request)
        print(list_display)
        list_display = list(list_display) + ('send_translation_request',)

        return list_display