from __future__ import print_function, unicode_literals

import os
import sys
from codecs import open
from hashlib import sha1
from itertools import chain
from shutil import rmtree

from django.conf import settings
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from rna.models import Release


OUTPUT_DIR = os.path.join(settings.ROOT, 'yaml_export')
SYS_REQ_MAP = {}


def get_sys_req_id(release):
    return sha1(release.system_requirements).hexdigest()


def setup():
    rmtree(OUTPUT_DIR, ignore_errors=True)
    rel_dir = os.path.join(OUTPUT_DIR, 'releases')
    sys_dir = os.path.join(OUTPUT_DIR, 'system-requirements')
    os.mkdir(OUTPUT_DIR)
    os.mkdir(rel_dir)
    os.mkdir(sys_dir)
    return rel_dir, sys_dir


def get_file_name(release):
    product = release.product
    channel = release.channel
    if product.lower() == 'firefox extended support release':
        product = 'firefox'
        channel = 'esr'
    return '{}-{}-{}'.format(
        product.lower().replace(' ', '-'),
        channel.lower(),
        release.version,
    )


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # start fresh
        rel_dir, sys_dir = setup()
        rel_count = 0
        sys_count = 0
        for rel in Release.objects.all():
            base_file_name = get_file_name(rel)
            sys_req_hash = get_sys_req_id(rel)
            if sys_req_hash in SYS_REQ_MAP:
                sys_req_id = SYS_REQ_MAP[sys_req_hash]
            else:
                SYS_REQ_MAP[sys_req_hash] = base_file_name
                sys_req_id = base_file_name
                sys_count += 1
                with open(os.path.join(sys_dir, '{}.md'.format(base_file_name)), 'w', encoding='utf-8') as fp:
                    fp.write(rel.system_requirements)

            with open(os.path.join(rel_dir, '{}.yml'.format(base_file_name)), 'w', encoding='utf-8') as fp:
                fp.write(render_to_string('rna/release.yml', {
                    'release': rel,
                    'notes': chain(*rel.notes(public_only=False)),
                    'system_requirements': sys_req_id,
                }))

            sys.stdout.write('.')
            sys.stdout.flush()
            rel_count += 1

        print('\n\nExported {} releases and {} system requirements'.format(rel_count, sys_count))
