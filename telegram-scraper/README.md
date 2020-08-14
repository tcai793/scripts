# Telegram-Scraper

## Requirement
Python package:
telethon

## Structure


## Note
two album may interleave. i.e. first message belongs to album A, second belongs 
to album B, but third belongs to album A again

It is NOT true that in an album only the first message has text and remainings
have no text

It is NOT true that in an album all messages' text are the same(ignoring empty),
but for most case capturing the first message's text should be enough