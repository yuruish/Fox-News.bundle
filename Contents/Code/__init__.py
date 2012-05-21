BASE_URL  = 'http://video.foxnews.com'
RSS_FEED  = '%s/v/feed/playlist/%%s.xml' % BASE_URL
VIDEO_URL = 'http://video.foxnews.com/v/%s'
RSS_NS    = {'mvn':'http://maven.net/mcr/4.1', 'media':'http://search.yahoo.com/mrss/'}

TITLE = 'Fox News'

ART  = 'art-default.png'
ICON = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'

###################################################################################################
def Start():
  Plugin.AddPrefixHandler('/video/foxnews', MainMenu, TITLE, ICON, ART)

  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)
  ObjectContainer.view_group = 'List'

  DirectoryObject.art = R(ART)
  DirectoryObject.thumb = R(ICON)

  HTTP.CacheTime = 1800
  HTTP.Headers['User-Agent']  = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13'

###################################################################################################
def MainMenu():
  oc = ObjectContainer()

  i = 0
  frontpage = HTML.ElementFromURL(BASE_URL, errors='ignore')
  for category in frontpage.xpath('//span[@class="arrow-up"]'):
    title = category.xpath('./a')[0].text.strip()
    i = i + 1
    oc.add(DirectoryObject(key = Callback(Category, i = i, title = title), title = title))

  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.foxnews", title = 'Search', summary = 'Search Videos...', prompt = 'Search:', thumb = R(ICON_SEARCH)))
  return oc

###################################################################################################
def Category(i, title):
  oc = ObjectContainer(title2 = title)

  frontpage = HTML.ElementFromURL(BASE_URL, errors='ignore')
  for sub in frontpage.xpath('//div[@id="playlist-2"]/ul[' + str(i) + ']/li'):
    try:
      title = sub.xpath('./a')[0].text.strip()
      playlist_id = sub.xpath('./a')[0].get('href').rsplit('-',1)[1]
      oc.add(DirectoryObject(key = Callback(Playlist, playlist_id = playlist_id, title = title), title = title))
    except:
      pass 
  return oc

###################################################################################################
def Playlist(playlist_id, title):
  oc = ObjectContainer(title2 = title, view_group = 'InfoList')
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
      thumb = Callback(Thumb, url = thumb_url),
      duration = duration,
      originally_available_at = date))

  if len(oc) == 0:
    return MessageContainer('Empty', "There aren't any items")
  else:
    return oc

###################################################################################################
def Thumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON))
