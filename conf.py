import logging
import os

#~ https://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/description.xml

ADDIN_VERSION = '2.7.3'
ADDIN_NAME = 'EasyDev'
FILE_OXT = '{}_v{}.oxt'.format(ADDIN_NAME, ADDIN_VERSION)
FILE_UPDATE = '{}.update.xml'.format(ADDIN_NAME.lower())
ADDIN_ID = "org.universolibre.EasyDev"
ADDIN_AUTHOR_WEB = "http://www.universolibre.org"
ADDIN_AUTHOR_NAME = "Universo Libre Mexico, A.C."
ADDIN_PLATFORM = 'all'
ADDIN_DEPENDENCIES_MINIMAL = '4.0'

GITHUB = 'https://github.com/UniversoLibreMexicoAC/easydev'
GITHUB_RAW = 'https://raw.github.com/UniversoLibreMexicoAC/easydev/master/files/'
ADDIN_UPDATE_XML = '{}{}'.format(GITHUB_RAW, FILE_UPDATE)
ADDIN_UPDATE_OXT = '{}/raw/v{}/files/{}'.format(GITHUB, ADDIN_VERSION, FILE_OXT)

ADDIN_ICON = 'images/{}.png'.format(ADDIN_NAME.lower())
ADDIN_LICENCE_ACCEPT_BY = 'user'  # or admin
ADDIN_LICENCE_SUPPRESS_ON_UPDATE = True
ADDIN_RELEASE_NOTES = True
ADDIN_DESCRIPTION = True
ADDIN_INFO = {
    'en': {
        'author': (ADDIN_AUTHOR_WEB, ADDIN_AUTHOR_NAME),
        'display_name': 'EasyDev - Tool for easy develop macros in LibreOffice, with Python',
        'license_text': 'registration/license_en.txt',
        'release_notes': '{}release-notes_en.txt'.format(GITHUB_RAW),
        'extension_description': 'description/desc_en.txt',
    },
    'es': {
        'author': (ADDIN_AUTHOR_WEB, ADDIN_AUTHOR_NAME),
        'display_name': 'EasyDev - Herramientas para desarrollo simple en LibreOffice, con Python',
        'license_text': 'registration/license_es.txt',
        'release_notes': '{}release-notes_es.txt'.format(GITHUB_RAW),
        'extension_description': 'description/desc_es.txt',
    },
    'fr': {
        'author': (ADDIN_AUTHOR_WEB, ADDIN_AUTHOR_NAME),
        'display_name': 'EasyDev - Outil pour faciliter le développement de macros dans LibreOffice, avec Python',
        'license_text': 'registration/license_en.txt',
        'release_notes': '{}release-notes_en.txt'.format(GITHUB_RAW),
        'extension_description': 'description/desc_fr.txt',
    },
}

FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE = '%d/%m/%Y %H:%M:%S'
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt=DATE)
LOG = logging.getLogger(ADDIN_NAME)

PATH_IDLC = '/usr/lib/libreoffice/sdk/bin/idlc'
PATH_IDLC_INCLUDE = '/usr/share/idl/libreoffice'
PATH_REGMERGE = '/usr/lib/libreoffice/ure/bin/regmerge'  # LibO 4
if not os.path.exists(PATH_REGMERGE):
    PATH_REGMERGE = '/usr/lib/libreoffice/program/regmerge'  # Libo 5

FILE_PY = '{}.py'.format(ADDIN_NAME)
FILE_IDL = 'X{}.idl'.format(ADDIN_NAME)
FILE_URD = 'X{}.urd'.format(ADDIN_NAME)
FILE_RDB = 'X{}.rdb'.format(ADDIN_NAME)
FILE_MANIFEST = 'manifest.xml'
FILE_DESCRIPTION = 'description.xml'
DIR_META = 'META-INF'
DIR_SOURCE = 'source'
DIR_FILES = 'files'

XML_MANIFEST = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest>
    <manifest:file-entry manifest:full-path="EasyDevLib/" manifest:media-type="application/vnd.sun.star.basic-library"/>
    <manifest:file-entry manifest:full-path="{}" manifest:media-type="application/vnd.sun.star.uno-component;type=Python"/>
    <manifest:file-entry manifest:full-path="{}" manifest:media-type="application/vnd.sun.star.uno-typelibrary;type=RDB"/>
    <manifest:file-entry manifest:full-path="config.xcs" manifest:media-type="application/vnd.sun.star.configuration-schema"/>
    <manifest:file-entry manifest:full-path="config.xcu" manifest:media-type="application/vnd.sun.star.configuration-data"/>
</manifest:manifest>
""".format(FILE_PY, FILE_RDB)

ICON = ''
if ADDIN_ICON:
    ICON = """
    <icon>
        <default xlink:href="{}" />
    </icon>""".format(ADDIN_ICON)

DEPENDENCIES = ''
if ADDIN_DEPENDENCIES_MINIMAL:
    DEPENDENCIES = """
    <dependencies>
        <OpenOffice.org-maximal-version value="4.x" d:name="OpenOffice.org 4.x" d:OpenOffice.org-minimal-version="{0}"/>
    </dependencies>""".format(ADDIN_DEPENDENCIES_MINIMAL)

UPDATE = ''
if ADDIN_UPDATE_XML:
    UPDATE = """
    <update-information>
        <src xlink:href="{0}" />
    </update-information>""".format(ADDIN_UPDATE_XML)

REGISTRATION = """
    <registration>
        <simple-license accept-by="{0}" suppress-on-update="{1}" >
            {{}}
        </simple-license>
    </registration>""".format(ADDIN_LICENCE_ACCEPT_BY, str(ADDIN_LICENCE_SUPPRESS_ON_UPDATE).lower())

PUBLISHER = ''
if ADDIN_AUTHOR_NAME:
    PUBLISHER = """
    <publisher>
        {}
    </publisher>"""

RELEASE_NOTES = ''
if ADDIN_RELEASE_NOTES:
    RELEASE_NOTES = """
    <release-notes>
        {}
    </release-notes>"""

ADDIN_DISPLAY_NAME = """
    <display-name>
        {}
    </display-name>"""

EXTENSION_DESCRIPTION = ''
if ADDIN_DESCRIPTION:
    EXTENSION_DESCRIPTION = """
    <extension-description>
        {}
    </extension-description>"""

DESCRIPTION = ''
DISPLAY_NAME = ''
NOTES = ''
ADDIN_AUTHOR = ''
LICENSE_TEXT = ''
for lang, options in ADDIN_INFO.items():
    for k, v in options.items():
        if k == 'license_text':
            LICENSE_TEXT += '<license-text xlink:href="{}" lang="{}" />' \
                '\n\t\t\t'.format(v, lang)
        elif k == 'author':
            ADDIN_AUTHOR += '<name xlink:href="{0}" lang="{1}">{2}</name>' \
                '\n\t\t'.format(v[0], lang, v[1])
        elif k == 'release_notes':
            NOTES += '<src xlink:href="{0}" lang="{1}" />\n\t\t'.format(v, lang)
        elif k == 'display_name':
            DISPLAY_NAME += '<name lang="{0}">{1}</name>\n\t\t'.format(lang, v)
        elif k == 'extension_description':
            DESCRIPTION += '<src xlink:href="{0}" lang="{1}" />\n\t\t'.format(v, lang)

REGISTRATION = REGISTRATION.format(LICENSE_TEXT)
PUBLISHER = PUBLISHER.format(ADDIN_AUTHOR)
RELEASE_NOTES = RELEASE_NOTES.format(NOTES)
ADDIN_DISPLAY_NAME = ADDIN_DISPLAY_NAME.format(DISPLAY_NAME)
EXTENSION_DESCRIPTION = EXTENSION_DESCRIPTION.format(DESCRIPTION)

XML_DESCRIPTION = """<?xml version="1.0" encoding="UTF-8"?>
<description
    xmlns="http://openoffice.org/extensions/description/2006"
    xmlns:d="http://openoffice.org/extensions/description/2006"
    xmlns:xlink="http://www.w3.org/1999/xlink">

    <version value="{0}" />
    <identifier value="{1}" />
    <platform value="{2}" />
    {3}
    {4}
    {5}
    {6}
    {7}
    {8}
    {9}
    {10}
</description>
""".format(ADDIN_VERSION, ADDIN_ID, ADDIN_PLATFORM, ICON, DEPENDENCIES, UPDATE,
    REGISTRATION, PUBLISHER, RELEASE_NOTES, ADDIN_DISPLAY_NAME, EXTENSION_DESCRIPTION)

XML_UPDATE = """<?xml version="1.0" encoding="UTF-8"?>
<description
    xmlns="http://openoffice.org/extensions/update/2006"
    xmlns:d="http://openoffice.org/extensions/description/2006"
    xmlns:xlink="http://www.w3.org/1999/xlink">

    <identifier value="{0}" />
    <version value="{1}" />
    {2}

    <update-download>
        <src xlink:href="{3}"/>
    </update-download>
    <release-notes>
        {4}
    </release-notes>

</description>""".format(ADDIN_ID, ADDIN_VERSION, '', ADDIN_UPDATE_OXT,
    RELEASE_NOTES)
