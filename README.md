# Discord History Search
 Searches discord server for mention of keywords

# How to use?

First install required python modules

```
python -m pip install -r requirements.txt
```

You also need [geckodriver (firefox)](https://github.com/mozilla/geckodriver/releases) installed

```
from discord_search import search
```

```
search(1234567891234567891, 'Example search', 'months', '2018-2-1', '2021-6-23')
```

You can also search by days, so that would be

```
search(1234567891234567891, 'Example search', 'days', '2018-2-1', '2021-6-23')
```

# .env
.env should have all of your discord login information and ratelimit time

```
LOGIN="example@example.com"
PASSWORD="password"
RATELIMIT=0.01
```