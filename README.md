# AnalyticsServer

Server pro analytická data pro Influencers aplikaci.

## Engagement rate

Výpočet se počítá jako
celkový počet liků + shares + comments + views / followers * 100

## Funkce API Serveru

Celý průběh spuštění serveru až po získávání dat a následné získávání dat z META/TT.

1. spuštění serveru pomocí python server.py nebo nějaké WSGI
2. počáteční inicializace a konfigurace
   1. vytvoření Flask aplikace
   2. nastavení připojení k DB
   3. nastavení CORS
   4. inicializace DB ve Flask aplikaci
   5. registrace API cest
   6. vytvoření tabulek s pomocí SQLAlchemy
3. počáteční získání dat z creators
   1. získání všech uživatelů -> uložení do DB (GET /api/api-influencers/creators)
      1. ukládám si email a id z creators, aby bylo pak možné jednoznačně spárovat s Creators appkou
   2. získání všech kampaní -> uložení do DB (GET /api/api-influencers/campaigns)
4. vytvoření plánovače
5. naplánování úloh <!-- TODO: zde je potřeba to vymyslet důkladně a přesně -->
   1. úloha, která bude každých 24 hodin získávat data z META/TT API
      1. znovu získá všechny uživatele z Creators a uloží nové do DB
      2. znovu získá všechny kampaně z Creators a uloží nové do DB
      3. fetch všech kampaní z DB, kde datum now >= start_date a zároveň now <= end_date
      4. vyfiltrování všech kampaní a získání jejich ID (jen ty u kterých budu hledat)
      5. fetch involved lidí ke kampaním
      6. získání všech příspěvků od uživatelů, projití popisu a nalezení hashtagů a uložení do DB
      7. 
      8. pro všechny kampaně, kde když bude now === end_date, tak ended = true
6. 
   <!-- 1. myslel bych si, že když kampaň bude od např. 10/7 - 20/8, tak bude zahrnuta v 7 i 8 měsíci, takže v době, kdy bude probíhat fetchování z DB, tak se nastaví příznak ended v době, kdy 
   1.  -->
7. <!-- TODO: --> instantní provedení 24h úlohy po spuštění nebo vyčkání na konkrétní čas
8. uložení dat z příspěvků do DB, tak abych věděl,

Z CALLU:

Zajímají mě data z kampaní jen od začátku publishing, takže už znám ty uživatele - involved v kampani
end publishing + 14 dnů budu řešit, pak campaing -> ended = true

<!-- TODO: Dobrá věc je to, že nevím jaká je timezone na serveru, takže časy bude potřeba zkontrolovat -->

ENDPOINT - PERMISSIONS
USAGE

1) META
GET https://graph.facebook.com/v.23/<FACEBOOK_USER_ID>/accounts | pages_show_list

* We use this endpoint to obtain <FACEBOOK_PAGE_ID> to obtain <IG_USER_ID>.

GET https://graph.facebook.com/v.23/<FACEBOOK_PAGE_ID> | pages_read_engagement, pages_show_list

* We use this endpoint to obtain <IG_USER_ID>. 
* fields = instagram_business_account, username

GET https://graph.facebook.com/v.23/<IG_USER_ID> | instagram_basic, pages_read_engagement, ads_read

* We use this endpoint to obtain profile information and statistics in order to complete user profiles in our application and obtain metrics about users and their potential reach.
* fields = followers_count, media_count, profile_picture_url

GET https://graph.facebook.com/v.23/<IG_USER_ID> | instagram_basic, pages_show_list

* We use this endpoint to retrieve media shared by the user and search for media whose description contains hashtags from campaigns the user has joined.
* fields = business_discovery.username(<IG_USERNAME>){{followers_count,media_count,media{{like_count,comments_count,permalink,thumbnail_url,timestamp,view_count,media_product_type,caption}}}}

GET https://graph.facebook.com/v.23/<IG_USER_ID>/stories | instagram_basic, pages_read_engagement, ads_read

* We use this endpoint to retrieve stories shared by the user and search for stories whose description contains hashtags from campaigns the user has joined.
* fields = id, permalink, media_type, timestamp, thumbnail_url, like_count, comments_count, caption

GET https://graph.facebook.com/v.23/<IG_MEDIA_ID>/insights | instagram_basic, instagram_manage_insights, pages_read_engagement, ads_read

* We use this endpoint to retrieve insights data about IG_MEDIA. 
* fields = id,permalink,media_type,timestamp,thumbnail_url,like_count,comments_count
* metric = impressions,reach,taps_forward,taps_back,exits,replies

1) TikTok
POST https://open.tiktokapis.com/v2/oauth/token/ | -

* We use this endpoint to get a token or renew token.

GET https://open.tiktokapis.com/v2/user/info/ | user.info.basic, user.info.profile, user.info.stats

* We use this endpoint to obtain profile information and statistics in order to complete user profiles in our application and obtain metrics about users and their potential reach.
* fields = open_id, avatar_url, display_name, profile_deep_link, username, follower_count, likes_count, video_count

POST https://open.tiktokapis.com/v2/video/list/ | video.list

* We use this endpoint to retrieve videos shared by the user and search for videos whose description contains hashtags from campaigns in which the user is signed up.
* fields = id, create_time, cover_image_url, video_description, embed_link, like_count, comment_count, share_count, view_count

## Co bude možná potřeba udělat

Problém nejspíš bude to, jak se právě teď získávají data o profilech tzn. chci všechny možné věci.
Problém může být v tom, že možná nebudu moct získat všechny údaje, ze kterých bych dostal všehny 
analytická data.
