import argparse
import os
import sys
import requests
from zipfile import ZipFile
from StringIO import StringIO
from xml.dom import minidom


def color(n):
    if n == 100:
        return 'brightgreen'
    if n > 90:
        return 'green'
    if n > 75:
        return 'yellowgreen'
    if n > 50:
        return 'yellow'
    if n > 25:
        return 'orange'
    return 'red'


def main():

    parser = argparse.ArgumentParser(
        description='Uploads html coverage directory to dropbox'
    )

    parser.add_argument(
        '--bitbaloon-access-token',
        type=str,
        help='',
        required=True
    )

    parser.add_argument(
        '--bitbaloon-site-name',
        type=str,
        help='',
        required=True
    )

    parser.add_argument(
        'path',
        metavar='html-dir-path',
        type=str,
        help='Local path where the coverage html directory is stored',
    )

    parser.add_argument(
        '--generate-shieldsio',
        action='store_true',
        help='Auto generate shildsio',
    )

    parser.add_argument(
        '--coverage-xml-path',
        type=str,
        help='',
        default="coverage.xml"
    )

    args = parser.parse_args()

    sitename = args.bitbaloon_site_name

    if args.generate_shieldsio:
        xmldoc = minidom.parse(args.coverage_xml_path)
        covelem = xmldoc.getElementsByTagName('coverage')[0]

        su = 'coverage branch'
        st = float(covelem.attributes['branch-rate'].value)*100
        co = color(st)
        st = '{}%'.format(int(st))
        url = 'https://img.shields.io/badge/{}-{}-{}.svg'.format(su, st, co)
        page = requests.get(url)
        with open('{}/coverage-branch.svg'.format(args.path), 'wb') as badge:
            badge.write(page.content)

        su = 'coverage lines'
        st = float(covelem.attributes['line-rate'].value)*100
        co = color(st)
        st = '{}%'.format(int(st))
        url = 'https://img.shields.io/badge/{}-{}-{}.svg'.format(su, st, co)
        page = requests.get(url)
        with open('{}/coverage-lines.svg'.format(args.path), 'wb') as badge:
            badge.write(page.content)

    print '> zipping html'

    inMemoryZip = StringIO()
    zf = ZipFile(inMemoryZip, 'w')
    for dirname, subdirs, files in os.walk(args.path):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename), filename)
    zf.close()
    inMemoryZip.seek(0)

    print '> checking if bitbaloon site name is available'

    r = requests.get(
        'https://www.bitballoon.com/api/v1/sites',
        params={'access_token': args.bitbaloon_access_token}
    )

    sid = None
    for s in r.json():
        if s['name'] == sitename:
            sid = s['id']

    if sid:
        print '> bitbaloon site with name {} found online (id: {})'.format(
            sitename, sid
        )
        print '> deleting bitbaloon site "{}"'.format(sid)
        r = requests.delete(
            'https://www.bitballoon.com/api/v1/sites/{}'.format(sid),
            params={'access_token': args.bitbaloon_access_token}
        )
        print '> deleted bitbaloon site "{}"'.format(sid)
    else:
        print 'bitbaloon site "{}" seems to be available'.format(sitename)

    print '> uploading to bitbaloon'

    r = requests.post(
        'https://www.bitballoon.com/api/v1/sites',
        params={'access_token': args.bitbaloon_access_token},
        files={'zip': ('landing.zip', inMemoryZip, 'application/zip')}
    )

    sid = r.json()['id']
    print '> created bitbaloon site {}'.format(sid)
    print '> changing name'

    r = requests.patch(
        'https://www.bitballoon.com/api/v1/sites/{}'.format(sid),
        params={'access_token': args.bitbaloon_access_token},
        data={'name': sitename}
    )

    print 'finish'


if __name__ == '__main__':
    main()
