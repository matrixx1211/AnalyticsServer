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
