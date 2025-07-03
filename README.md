June 20, 2025 = Day 5 of learning Python

_"Write it in English, translate it to Python"._

***
## Get the next UFC event
To get the upcoming UFC event:

```python
cd next_event/next_event
```
then:
```python
py -m scrapy crawl event
```

## Import and format it:

``` python
py odds_scraper.py
```
If the event changes, fight is canceled, fighter drops of the card etc... , just re-run the above code to get
 the updates.
 
## Update the odds from draftkings:

``` python
py odds_updater.py
```
Please note: Never run the updater when a fight is live.
***
Additional info in the [wiki](https://github.com/socialatm/draftkings/wiki)
