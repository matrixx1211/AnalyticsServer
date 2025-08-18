# Všechny důležité informace k TikTok API

Informace o tom, co je potřeba k těm requestům na TikTok a jaký je workflow.
CODE má expire time velmi nízký nevím kolik???
ACCESS_TOKEN má expire time většinou 1 den (86 400), potřeba obnovovat každý den za pomocí REFRESH_TOKEN.
REFRESH_TOKEN má expire time většinou 1 rok (365 * 86 400), nevím zde, jak obnovit. (MOŽNÁ STAČÍ UDĚLAT REFRESH_ACCESSu a tím se obnoví zase na rok)

## Získání CODE (kroky 1, 2) a TOKENu pomocí CODE (kroky 3, 4)

1. přihlášení 
2. návrat na redirect_uri s ?code=...
3. požádání o token s pomocí code
4. získání -> access_token, refresh_token, expires_in, refresh_expires_in, scope, token_type

## Získání TOKENu pomocí REFRESH TOKENu

1. požádání o token s pomocí refresh_token
2. nový access_token