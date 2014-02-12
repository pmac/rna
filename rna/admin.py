# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django import forms
from django.contrib import admin
from pagedown.widgets import AdminPagedownWidget

from . import models


class NoteAdminForm(forms.ModelForm):
    note = forms.CharField(widget=AdminPagedownWidget())

    class Meta:
        model = models.Note


class NoteAdmin(admin.ModelAdmin):
    form = NoteAdminForm
    list_display = ('bug', 'tag', 'note', 'created')
    list_display_links = ('note',)
    list_filter = ('tag', 'is_known_issue')
    filter_horizontal = ('releases',)
    search_fields = ('bug', 'note', 'releases__version')


class NoteInline(admin.TabularInline):
    model = models.Note.releases.through
    extra = 1
    raw_id_fields = ('note',)


class ReleaseAdminForm(forms.ModelForm):
    system_requirements = forms.CharField(widget=AdminPagedownWidget())
    text = forms.CharField(widget=AdminPagedownWidget())
    release_date = forms.DateTimeField(widget=admin.widgets.AdminDateWidget)

    class Meta:
        model = models.Release


class ReleaseAdmin(admin.ModelAdmin):
    form = ReleaseAdminForm
    inlines = (NoteInline,)
    list_display = ('version', 'product', 'channel', 'is_public',
                    'release_date', 'text')
    list_filter = ('product', 'channel', 'is_public')
    ordering = ('-release_date',)
    search_fields = ('version', 'text')


admin.site.register(models.Note, NoteAdmin)
admin.site.register(models.Release, ReleaseAdmin)
