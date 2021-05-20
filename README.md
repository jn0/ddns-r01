# ddns-r01

sorta DDNS using [partners' API of r01.ru](https://help.r01.ru/partner/api.html)

When the script is ran, it loads config, checks its current IP address (at a [public service](https://github.com/mpolden/echoip)),
finds the domain, extracts its resource records, checks if the A-record has the same IP, and "edits" it if new IP observed.
If the domain has no A-record, then the new entry is inserted.

----

«Типа, DDNS» на [партнёрском API регистратора r01](https://help.r01.ru/partner/api.html)

При запуске скрипта он читает свой конфиг, ищет текущий IP (опросом [публичного сервиса](https://github.com/mpolden/echoip)),
ищет свой домен у регистратора, вынимает ресурсные записи домена, проверяет, что A-запись имеет тот же IP и "редактирует" её
если полученный IP — новый. Если домен не имеет A-записи, то она добавляется.

# EOF #
