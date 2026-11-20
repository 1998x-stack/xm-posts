"""RSS 2.0 contract: stable IDs, safe XML, date precision and discoverability."""
from datetime import date, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import sys
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_site import DEFAULT_URL, article_url, build_feed, data, enrich_article_head, html_page, url_join

ATOM_NS='http://www.w3.org/2005/Atom'
DCTERMS_NS='http://purl.org/dc/terms/'


def test_feed_contains_exactly_published_posts_and_valid_metadata():
    categories,posts=data(ROOT)
    published=[p for p in posts if p['status']=='published']
    xml=build_feed(categories,posts,DEFAULT_URL)
    root=ET.fromstring(xml)
    assert root.tag=='rss' and root.get('version')=='2.0'
    channel=root.find('channel')
    assert channel is not None
    assert channel.findtext('title')=='xm-posts'
    assert channel.findtext('link')==DEFAULT_URL
    assert channel.findtext('language')=='zh-cn'
    assert channel.findtext('description')
    assert channel.find(f'{{{ATOM_NS}}}link').attrib=={
        'href':url_join(DEFAULT_URL,'feed.xml'),
        'rel':'self',
        'type':'application/rss+xml',
    }
    items=channel.findall('item')
    assert len(items)==len(published)
    urls=[item.findtext('guid') for item in items]
    assert len(set(urls))==len(urls)
    by_url={item.findtext('guid'):item for item in items}
    assert set(by_url)=={url_join(DEFAULT_URL,article_url(p)) for p in published}
    expected_order=sorted(published,key=lambda p:(p['updated'],p['published'],p['slug']),reverse=True)
    assert urls==[url_join(DEFAULT_URL,article_url(p)) for p in expected_order]

    for p in published:
        url=url_join(DEFAULT_URL,article_url(p))
        item=by_url[url]
        assert item.findtext('title')==p['title']
        assert item.findtext('description')==p['summary']
        assert item.findtext('link')==url
        assert item.find('guid').get('isPermaLink')=='true'
        stamp=parsedate_to_datetime(item.findtext('pubDate'))
        assert stamp.tzinfo is not None
        assert stamp.astimezone(timezone.utc).date()==date.fromisoformat(p['published'])
        assert (stamp.hour,stamp.minute,stamp.second)==(0,0,0)
        assert item.findtext(f'{{{DCTERMS_NS}}}modified')==p['updated']
        categories_in_feed=item.findall('category')
        assert len(categories_in_feed)==2
        assert categories_in_feed[0].get('domain')==url_join(DEFAULT_URL,f'categories/{p["category"]}/')
        assert categories_in_feed[1].get('domain')==url_join(
            DEFAULT_URL,f'categories/{p["category"]}/#topic-{p["topic"]}'
        )


def test_feed_escapes_xml_and_never_emits_drafts():
    categories,posts=data(ROOT)
    source=next(p for p in posts if p['status']=='published')
    visible={**source,'title':'Q & A <Feed>','summary':'中文 & symbols < > " quotes'}
    hidden={**source,'slug':'not-public','title':'TOP SECRET DRAFT','status':'draft'}
    xml=build_feed(categories,[hidden,visible],DEFAULT_URL)
    root=ET.fromstring(xml)
    items=root.findall('./channel/item')
    assert len(items)==1
    assert items[0].findtext('title')==visible['title']
    assert items[0].findtext('description')==visible['summary']
    assert 'TOP SECRET DRAFT' not in xml
    assert '&amp;' in xml and '&lt;' in xml
    assert build_feed(categories,[hidden,visible],DEFAULT_URL)==xml


def test_home_and_individual_article_advertise_feed_without_duplicates():
    categories,posts=data(ROOT)
    p=next(p for p in posts if p['status']=='published')
    home=html_page(
        title='RSS discovery',description='test',canonical=DEFAULT_URL,
        body='<h1>RSS discovery</h1>',
    )
    home_doc=BeautifulSoup(home,'html.parser')
    home_feed=home_doc.find_all('link',attrs={'rel':'alternate','type':'application/rss+xml'})
    assert len(home_feed)==1
    assert home_feed[0]['href']=='feed.xml'

    original='<html><head><title>Post</title></head><body><main><h1>Post</h1></main></body></html>'
    enriched=enrich_article_head(original,p,DEFAULT_URL)
    twice=enrich_article_head(enriched,p,DEFAULT_URL)
    soup=BeautifulSoup(twice,'html.parser')
    article_feeds=soup.find_all('link',attrs={'rel':'alternate','type':'application/rss+xml'})
    assert len(article_feeds)==1
    assert article_feeds[0]['href']==url_join(DEFAULT_URL,'feed.xml')
