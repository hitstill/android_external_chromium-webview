from xml.dom import minidom, pulldom

import requests_cache

requests_session = requests_cache.CachedSession('updater', backend='memory')


class ApkRelease:
    version_name: str
    version_code: int
    download_url: str

    def __init__(self, version_name: str, version_code: int, download_url: str):
        self.version_name = version_name
        self.version_code = version_code
        self.download_url = download_url


def _child_el_content(el: minidom.Element, tag_name: str):
    return el.getElementsByTagName(tag_name).item(0).firstChild.data


def fdroid_recommended_release(repo: str, application_id: str):
    with requests_session.get('{}/index.xml'.format(repo)) as r:
        doc = pulldom.parseString(r.text)
        apks = []
        for event, node in doc:
            if event == pulldom.START_ELEMENT and node.tagName == 'application':
                if node.getAttribute('id') == application_id:
                    doc.expandNode(node)
                    marketvercode = _child_el_content(node, 'marketvercode')
                    for p in node.getElementsByTagName('package'):
                        if _child_el_content(p, 'versioncode') == marketvercode:
                            return ApkRelease(
                                _child_el_content(p, 'version'),
                                int(marketvercode),
                                '{}/{}'.format(repo, _child_el_content(p, 'apkname'))
                            )
        raise Exception('Did not find {} in repo {}'.format(application_id, repo))


def fdroid_latest_release(repo: str, application_id: str, nativecode: str):
    with requests_session.get('{}/index.xml'.format(repo)) as r:
        doc = pulldom.parseString(r.text)
        apks = []
        for event, node in doc:
            if event == pulldom.START_ELEMENT and node.tagName == 'application':
                if node.getAttribute('id') == application_id:
                    doc.expandNode(node)
                    marketversion = _child_el_content(node, 'marketversion')
                    marketvercode = _child_el_content(node, 'marketvercode')
                    for p in node.getElementsByTagName('package'):
                        if _child_el_content(p, 'version') == marketversion and _child_el_content(p, 'nativecode') == nativecode:
                            return ApkRelease(
                                _child_el_content(p, 'version'),
                                int(marketvercode),
                                '{}/{}'.format(repo, _child_el_content(p, 'apkname'))
                            )
        raise Exception('Did not find {} in repo {}'.format(application_id, repo))

#https://fdroid.bromite.org/fdroid/repo/rel_103.0.5060.140_x64_SystemWebView.apk
