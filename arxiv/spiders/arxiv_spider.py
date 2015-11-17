# -*- coding: utf-8 -*-
from scrapy.spiders import XMLFeedSpider
from scrapy import Request

from arxiv.items import ArxivItem

class ArxivSpider(XMLFeedSpider):
    allowed_domains = ["inspirehep.net"]
    name = 'arxiv'
    start_urls = ["http://inspirehep.net/search?ln=pl&ln=pl&p=recid%3A%2F1290986%7C1290985%7C1283408%7C1290984%7C1290983%7C1296027%7C1296026%7C1296025%7C1290982%7C1296024%7C1296023%7C1290981%7C1290980%7C1296022%7C1290979%7C1290978%7C1296021%7C1290974%7C1290973%7C1296020%7C1296019%7C1290972%7C1290971%7C1296017%7C1296018%7C1296015%7C1290970%7C1290969%7C1296014%7C1290968%7C1290967%7C1290964%7C1290965%7C1296013%7C1290962%7C1290961%7C1290960%7C1290959%7C1290958%7C1296011%7C1296010%7C1296009%7C1296008%7C1296007%7C1296006%7C1296005%7C1296004%7C1326844%7C1326845%7C1326846%7C1306073%7C1306072%7C1306071%7C1306070%7C1300411%7C1396910%7C1306069%7C1306067%7C1306066%7C1311669%7C1306064%7C1306063%7C1306062%7C1306065%7C1311667%7C1311666%7C1311665%7C1311664%7C1311663%7C1311662%7C1311661%7C1316404%7C1316403%7C1316402%7C1316401%7C1316399%7C1316398%7C1316397%7C1316395%7C1321758%7C1321757%7C1326843%7C1326842%7C1326841%7C1326840%7C1326839%7C1326838%7C1326837%7C1327802%7C1327803%7C1334222%7C1334221%7C1334220%7C1334218%7C1334219%7C1334217%7C1334216%7C1334215%7C1334214%7C1338431%7C1345956%7C1345954%7C1345953%7C1365931%7C1365930%7C1365929%7C1365922%7C1365921%7C1365927%7C1365924%7C1365916%7C1365928%7C1365926%7C1365925%7C1365923%7C1365919%7C1365917%7C1365915%7C1365914%7C1383016%7C1383628%7C1383627%7C1383626%7C1383625%7C1383631%7C1383624%7C1383623%7C1383622%7C1383621%7C1383635%7C1383633%7C1383620%7C1383619%7C1383618%7C1387840%7C1383629%7C1383630%7C1383634%7C1382889%7C1387838%7C1387837%7C1387833%7C1393137%7C1393136%7C1394260%7C1396895%7C1396894%7C1396892%7C1396891%7C1396890%7C1396889%7C1396888%7C1396887%7C1396886%7C1397900%7C1400355%2F&action_search=Szukaj&sf=earliestdate&so=d&rm=&rg=200&sc=0&of=xme&wl=0"]
    #start_urls = ["http://inspirehep.net/search?ln=pl&ln=pl&p=recid%3A%2F1290986%7C1290985%7C1396895%2F&action_search=Szukaj&sf=earliestdate&so=d&rm=&rg=200&sc=0&of=xme&wl=0"]

    def parse(self, response):
        response.selector.remove_namespaces()

        def _process(author, recid):
            name = author.xpath('subfield[@code="a"]/text()').extract()[0]
            print type(name)
            print(name)
            identifier = author.xpath('subfield[@code="x"]/text()').extract()
            print("{2} === I have name: {0} and id: {1}".format(name.encode('utf-8'), identifier, recid))
            if identifier:
                print("Checking author")
                req = Request("http://inspirehep.net/record/{0}/export/xm".format(identifier[0]), callback=self.parse_author_id)
            else:
                print("Checking records for author")
                req = Request("http://inspirehep.net/search?ln=pl&ln=pl&p=author:{0} year:2014->2015&of=xm".format(name.encode('ascii', 'xmlcharrefreplace')), callback=self.parse_name)
            req.meta['recid'] = recid
            req.meta['author'] = {'name': unicode(name), 'id': identifier}
            return req

        for record in response.xpath('//record'):
            recid = record.xpath('controlfield[@tag="001"]/text()').extract()[0]
            for author in record.xpath('datafield[@tag="100"]'):
                yield _process(author, recid)
            for author in record.xpath('datafield[@tag="700"]'):
                yield _process(author, recid)

    def parse_author_id(self,response):
        response.selector.remove_namespaces()
        for n in response.xpath('//datafield[@tag="035"]'):
            if n.xpath('subfield[@code="9"]/text()').extract() == ['BAI']:
                name = n.xpath('subfield[@code="a"]/text()').extract()[0]
        if not name:
            name = response.meta['author']['name']
        req = Request("http://inspirehep.net/search?ln=pl&ln=pl&p=author:{0} year:2014->2015&of=xm".format(name.encode('ascii', 'xmlcharrefreplace')), callback=self.parse_name)
        req.meta['recid'] = response.meta['recid']
        req.meta['author'] = response.meta['author']
        req.meta['author']['name'] = unicode(name)
        yield req

    def parse_name(self, response):
        response.selector.remove_namespaces()
        all_articles = 0
        arxiv_articles = 0
        for record in response.xpath('//record'):
            all_articles += 1
            for field in record.xpath('datafield[@tag="035"]'):
                if field.xpath('subfield[@code="9"]/text()').extract() == ["arXiv"]:
                    arxiv_articles += 1
        with open("autorzy.txt", "a") as f:
            f.write("%s|%s|%s|%s|%s\n" % (response.meta['recid'], response.meta['author']['name'].encode('ascii', 'xmlcharrefreplace'), response.meta['author']['id'], all_articles, arxiv_articles))
        # print("%s %s %s %s %s" % (response.meta['recid'], response.meta['author']['name'].encode('utf-8'), response.meta['author']['id'], all_articles, arxiv_articles))
        # print all_articles, arxiv_articles
