BASE_URL  = 'http://video.foxnews.com'
NAV_URL   = BASE_URL + '/playlist/featured-latest-news/'
VIDEO_URL = BASE_URL +'/v/%s'

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

  for category in navpage.xpath('//div[@class="browse"]//ul/li/a[contains(@href, "/playlist/")]/parent::li'):
    title = category.xpath('./a')[0].text.strip()
    playlist_id = category.xpath('./a/@href')[0].split('playlist/')[1][:-1]
    oc.add(DirectoryObject(key=Callback(Shows, playlist_id=playlist_id, title=title), title=title))
    
  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.foxnews", title='Search', summary='Search Fox News Videos', prompt='Search:', thumb=R(ICON_SEARCH)))

  return oc

@route('/video/foxnews/shows/{playlist_id}')
def Shows(playlist_id, title):
  oc = ObjectContainer(title2 = title)
  playlist = HTML.ElementFromURL('%s/playlist/%s' % (BASE_URL , playlist_id))
  Log("playlist=%s" % playlist);
 
  oc.add(DirectoryObject(key=Callback(Playlist, playlist_id=playlist_id, title="All "+title), title="All "+title))
  for item in playlist.xpath('//div[@id="shows"]//ul/li'):
    new_playlist_id=item.xpath('./a/@href')[0].split('playlist/')[1][:-1]
    new_title=item.xpath('./a')[0].text.strip()
    oc.add(DirectoryObject(key=Callback(Playlist, playlist_id=new_playlist_id, title=new_title), title=new_title))

  if len(oc) == 1:
    return Playlist(playlist_id,title);
  else:
    return oc

###################################################################################################
@route('/video/foxnews/playlist/{playlist_id}')
def Playlist(playlist_id, title):

  oc = ObjectContainer(title2 = title)
  playlist = HTML.ElementFromURL('%s/playlist/%s' % (BASE_URL , playlist_id))
  for item in playlist.xpath('//div[@id="playlist"]//ul/li/div/a[contains(@href, "?playlist_id=")]/parent::div/parent::li'):
    title       = item.xpath('.//div[@class="info"]//a')[0].text.replace('&amp;', '&').strip()
    description = item.xpath('.//div[@class="info"]/p/span')[0].text.replace('&amp;', '&')
    duration    = item.xpath('.//div[@class="info"]/p/strong')[0].text
    duration    = (int(duration.split(':')[0])*60 + int(duration.split(':')[1])) * 1000
    date        = item.xpath('.//div[@class="info"]/time')[0].text
    date        = Datetime.ParseDate(date)
    thumb_url   = item.xpath('.//div[@class="m"]/a/img/@src')
    url         = item.xpath('.//div[@class="m"]/a/@href')[0]
    url         = 'http:' + url
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
