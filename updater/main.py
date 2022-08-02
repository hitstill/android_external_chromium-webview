import urllib.request
from os import path

import certificates
from sources import ApkRelease, fdroid_latest_release


def update_if_needed(arch: str, release: ApkRelease):
    module_dir = path.abspath(path.join(path.dirname(__file__), '..', 'prebuilt/{}/'.format(arch)))
    with open(path.join(module_dir, '.version_code'), 'r+') as version_code_file:
        version_code = int(version_code_file.read())
        if version_code < release.version_code:
            print('updating {} to {}'.format(arch, release.version_name))
            apk_filename = path.join(module_dir, 'webview.apk')

            old_sig = certificates.get_apk_certificate(apk_filename)

            print('downloading {} ...'.format(release.download_url))
            urllib.request.urlretrieve(release.download_url, apk_filename)

            new_sig = certificates.get_apk_certificate(apk_filename)
            if old_sig != new_sig:
                raise Exception('Signature mismatch for {} old sig: {} new sig: {}'.format(module, old_sig, new_sig))

            version_code_file.seek(0)
            version_code_file.write(str(release.version_code))
            version_code_file.truncate()
            version_code_file.close()

        elif version_code > release.version_code:
            print('{} ahead of suggested version ({} > {})'.format(module, version_code, release.version_code))
        elif version_code == release.version_code:
            print('{} up to date.'.format(module))

fdroid_bromite_repo = 'https://fdroid.bromite.org/fdroid/repo'

update_if_needed('arm64', fdroid_latest_release(fdroid_bromite_repo, 'org.bromite.webview', 'arm64-v8a'))
