## Brief Instruction (not tested)

1. Go to downloaded folder `gp`

2. Setup python environment
Although lots of packages in `requirement.txt` are actually not required, I just haven't cleaned up...

```
pip install -r requirements.txt
```

3. 
Because the reviews are loaded with JS, Selenium and Headless Chrome are required (with the former installed in step 2): https://sites.google.com/a/chromium.org/chromedriver/downloads

4. Install MongoDB

If don't want to use MongoDB, go to `settings.py` and find the pipelines setting. Uncomment the JSONpipeline and disable settings relating to MongoDB

```
ITEM_PIPELINES = {
   # 'gp.pipelines.GoogleplayspiderJSONPipeline': 300,
   'gp.pipelines.GoogleplayspiderMongoDBPipeline': 300,
}

MONGODB_URI = 'mongodb://127.0.0.1:27017'
MONGODB_DATABASE = 'healthmobileapp'
```

Also need to change the JSON file directory in `pipelines.py`:

```
#line 60
self.files = dict([ (name, open('yourDirecotry/' + name + '.json', 'wb')) for name in self.saveTypes]) 
```

5. Change app categories

The default program will skip apps that are not 'health' or 'medical'. You can change this in `line 73` of the `middlewares.py`.

6. Logging files directory

Log files directory is currently specified in `middlewares.py`. Please update accordingly.

7. Run the crawler

```
scrapy crawl gp_crawl
```


#### 参考
1. [Scrapy+Selenium+Headless Chrome的Google Play爬虫](https://www.jianshu.com/p/d64b13a2322b)
2. https://www.jianshu.com/p/411b20a5ce55

