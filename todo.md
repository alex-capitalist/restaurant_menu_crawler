# Issues
* Problems with the input files:
   * `"oct_menu": "Menu"` overlaps with literally every menu type on the list. Imo it should be renamed to something like `"oct_generic_menu": "Menu"`.
   * In a few cases restaurant links were provided with **http**, **and not https** "Miki": "http://miki.ch/" (cool site otherwise :-) )
   * only one restaurant had the cookies button - https://amrank.ch/


* include site map related files (e.g. /sitemap, /sitemap.xml)


* https://chez-smith.ch/de/
   * actual menu links are at the 3rd level, though we check only 2 levels deep
* La_Catedral:
   * (quickfix) if two menu links have conflicting names, then we should have all of them in the output file, we can have multiple instances of the same menu type.
Examples:
      * oct_drink https://www.lacatedral.ch/_files/ugd/f728f6_903a8e63ab654999a4d06bf473162a4c.pdf
      * oct_season https://www.lacatedral.ch/_files/ugd/f728f6_903a8e63ab654999a4d06bf473162a4c.pdf
      * oct_drink https://www.lacatedral.ch/_files/ugd/f728f6_60a2bf8cc8ad4224b3c8129182a87777.pdf
      * oct_brunch https://www.lacatedral.ch/_files/ugd/f728f6_5ae9b78a73524ae4bb2dff337ce3c2b2.pdf

   * there garbage link. On one side it is a different domain, but pdf can be hosted on different domains. Not clear what to do for now. Maybe parse at a later stage. "https://progallery.wix.com/worker.html?pageId=masterPage&compId=tpaWorker_1338&viewerCompId=tpaWorker_1338&siteRevision=254&viewMode=site&deviceType=desktop&locale=en&tz=Europe%2FZurich&regionalLanguage=en&endpointType=worker&instance=jKz9g84NwU4AJigGZkG3kSzLROvE_0xhcoWuKKJFbao.eyJpbnN0YW5jZUlkIjoiMmZkZTQyYmQtNTFhOS00MTA1LWI0NTYtMmRmNWU3YzhiZWI4IiwiYXBwRGVmSWQiOiIxNDI3MWQ2Zi1iYTYyLWQwNDUtNTQ5Yi1hYjk3MmFlMWY3MGUiLCJtZXRhU2l0ZUlkIjoiYzRiNzI1M2UtNDI4Mi00YmU2LThhM2UtZmJjZDdkODEyZWVjIiwic2lnbkRhdGUiOiIyMDI1LTA5LTA0VDA2OjQ4OjMxLjMzOVoiLCJkZW1vTW9kZSI6ZmFsc2UsImFpZCI6IjliMGI1NzM2LWI0YjctNGYwZS1hZTkyLWFjNzExMGQ2YzFjYyIsImJpVG9rZW4iOiJlYjY5Njc4My0xMzJiLTBhZTMtM2U2OC1kNjM4OWE0OTkwNTQiLCJzaXRlT3duZXJJZCI6ImY3MjhmNmEyLTdkOTYtNDkwMC1iZmQzLTQ2YTQwNjdmMGQzMCIsImJzIjoiY1dadHp2QTBZZEtYWmt2bDNvQTZVWmJ5akJVT0VkMlZJaUczc1VUTVl4YyIsInNjZCI6IjIwMjMtMDYtMjRUMDg6Mjk6MzcuNDI5WiJ9&currency=CHF&currentCurrency=CHF&commonConfig=%7B%22brand%22%3A%22wix%22%2C%22host%22%3A%22VIEWER%22%2C%22bsi%22%3A%22e4ecbc71-3031-4303-b20b-6b5b1ca81818%7C1%22%2C%22siteRevision%22%3A%22254%22%2C%22renderingFlow%22%3A%22NONE%22%2C%22language%22%3A%22en%22%2C%22locale%22%3A%22de-ch%22%2C%22BSI%22%3A%22e4ecbc71-3031-4303-b20b-6b5b1ca81818%7C1%22%7D&currentRoute=.%2Faboutus&vsi=105a2037-d82c-4ecc-bea9-4b9274c5ce7c"

* ~~(quickfix) Invoking agent - doesn't show an error if the server is down/error~~ ✅ FIXED

* https://www.lulu-zh.ch/
   * (maybe via prompt fix?) didn't find the path https://www.lulu-zh.ch/ *(automatic forward) ->* https://www.lulu-zh.ch/en **->** https://www.lulu-zh.ch/media/lulu_speisekarte_restaurant_a3_en_210725.pdf
   **->** https://www.lulu-zh.ch/media/lulu_weinkarte-de.pdf
   * called the model, no understanding why
   * "Integrated in the website" - it did't understand that there were additional actual menu pdf links

* https://www.hermanseck.ch/
   * **(can be filtered out in post processing, by the OCR model)** apart from the found pdf menu, it added menu item images to the list.

* "Daizy": "http://www.daizy.ch/",
   * Just nothing found, maybe we can try three nested levels

* "Gamper_Restaurant": "http://gamper-restaurant.ch/"
   * I have my doubts it is possible to find the menu without OCR. An perfect example of a terrible website: https://gamper-restaurant.ch/wermuteria 
   * (quickfix) use /sitemap.xml to get the link to the menu
   * (quickfix) use /sitemap.xml to get the link to the menu, if it opens, feed it to the model

* (quickfix) "Neue_Taverne": "https://neuetaverne.ch/"
   * Found all menus except the abend one: https://www.neuetaverne.ch/media//tav250731_abend_en__1.pdf