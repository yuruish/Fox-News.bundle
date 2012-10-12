BASE_URL = 'http://video.foxnews.com'
NAV_URL = 'http://video.foxnews.com/playlist/latest-video-latest-news/'
RSS_FEED = '%s/v/feed/playlist/%%s.xml' % BASE_URL
VIDEO_URL = 'http://video.foxnews.com/v/%s'
RSS_NS = {'mvn':'http://maven.net/mcr/4.1', 'media':'http://search.yahoo.com/mrss/'}

TITLE = 'Fox News'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'

###################################################################################################
def Start():

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)

  DirectoryObject.art = R(ART)
  DirectoryObject.thumb = R(ICON)

  HTTP.CacheTime = 1800

###################################################################################################
@handler("/video/foxnews", TITLE, thumb=ICON, art=ART)
def MainMenu():

  oc = ObjectContainer()
  navpage = HTML.ElementFromURL(NAV_URL)

  for category in navpage.xpath('//nav//ul/li'):
    title = category.xpath('./a')[0].text.strip()
    playlist_id = category.xpath('./a/@href')[0].split('playlist_id=')[1]
    oc.add(DirectoryObject(key=Callback(Playlist, playlist_id=playlist_id, title=title), title=title))
    
  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.foxnews", title='Search', summary='Search Videos...', prompt='Search:', thumb=R(ICON_SEARCH)))

  return oc

###################################################################################################
@route('/video/foxnews/playlist/{playlist_id}')
def Playlist(playlist_id, title):

  oc = ObjectContainer(title2 = title)
  playlist = XML.ElementFromURL(RSS_FEED % (playlist_id), errors='ignore').xpath('//item')

  for item in playlist:
    title       = item.xpath('./title')[0].text.replace('&amp;', '&').strip()
    description = item.xpath('.//media:description', namespaces=RSS_NS)[0].text.replace('&amp;', '&')
    duration    = item.xpath('./media:content/mvn:duration', namespaces=RSS_NS)[0].text
    duration    = int(duration) * 1000
    date        = item.xpath('./media:content/mvn:airDate', namespaces=RSS_NS)[0].text
    date        = Datetime.ParseDate(date)
    thumb_url   = item.xpath('./media:content/media:thumbnail', namespaces=RSS_NS)[0].text
    assert_id   = item.xpath('./media:content/mvn:assetUUID', namespaces=RSS_NS)[0].text
    url         = VIDEO_URL % assert_id

    oc.add(VideoClipObject(
      url = url, 
      title = title, 
      summary = description, 
      thumb=Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON),
      duration = duration,
      originally_available_at = date))

  if len(oc) == 0:
    return ObjectContainer('Empty', "There aren't any items")
  else:
    return oc
