from scrapy import cmdline

cmdline.execute("scrapy crawl gp -a urls='https://play.google.com/store/apps/details?id="
                "id.danarupiah.weshare.jiekuan&hl=id'".split())
