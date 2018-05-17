import scrapy
import re
from googletrans import Translator

class CurseForgeSpider(scrapy.Spider):
	name = "curse"
	# 不同Minecraft版本对应的URL
	urls = {
		'1.6.4': 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A326&filter-sort=4',
		'1.7.10': 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A4449&filter-sort=4',
		'1.8.9': 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A5806&filter-sort=4',
		'1.9.4': 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A6084&filter-sort=4',
		'1.10.2': 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A6170&filter-sort=4',
		'1.11.2': 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A6452&filter-sort=4',
		'1.12.2': 'https://www.curseforge.com/minecraft/mc-mods?filter-game-version=2020709689%3A6756&filter-sort=4',
	}
	start_urls = []
	try:
		version = input("请输入Minecraft版本号:")
		select_url = urls[version]
	except KeyError:
		print("不支持的版本号/未知输入！")
	start_urls.append(select_url)


	# 用于翻译分类信息
	@staticmethod
	def cate_trans(str_list):
		trans_dict = {
			'Addons': '附属',
			'Applied Energistics 2': '应用能源2',
			'Blood Magic': '血魔法',
			'Buildcraft': '建筑工艺',
			'Forestry': '林业',
			'Industrial Craft': '工业',
			'Thaumcraft': '神秘时代',
			'Thermal Expansion': '热力膨胀',
			'Tinker\'s Construct': '匠魂',
			'Adventure and RPG': '冒险与RPG',
			'Armor, Tools, and Weapons': '盔甲工具武器',
			'Cosmetic': '装饰',
			'Food': '食物',
			'Magic': '魔法',
			'Map and Information': '地图与信息',
			'Redstone': '红石',
			'Server Utility': '服务器工具',
			'Storage': '储存',
			'Technology': '科技',
			'Energy': '能量',
			'Energy, Fluid, and Item Transport': '物流',
			'Farming': '农业',
			'Genetics': '基因',
			'Player Transport': '玩家运输',
			'Processing': '处理',
			'Twitch Integration': 'Twitch集成',
			'World Gen': '世界生成',
			'Biomes': '生物群系',
			'Dimensions': '世界维度',
			'Mobs': '生物',
			'Ores and Resources': '矿物资源',
			'Structures': '建筑结构',
			'API and Library': 'API与库',
			'Miscellaneous': '杂项',
		}
		# 遍历列表，使用key在翻译字典中取value，取不到值时返回原文
		new_list = []
		for i in str_list:
			translation = trans_dict.get((i), i)
			new_list.append(translation)
		# 返回翻译后的列表
		return new_list


	def parse(self, response):
		li_tags = response.xpath('//li[@class="project-list-item"]')

		# 遍历所有匹配的li元素提取数据
		for li in li_tags:
			# mod名称，去除首尾空白字符，谷歌翻译
			name = li.xpath('.//h2[@class="list-item__title strong mg-b-05"]/text()').extract_first()
			name = name.strip()
			trans = Translator()
			name_cn = trans.translate(name, dest='zh-cn').text
			
			# mod所属分类，调用cate_trans()翻译
			category = li.xpath('.//div[@class="list-item__categories"]//a/@title').extract()
			category_cn = CurseForgeSpider.cate_trans(category)

			# 下载量
			download = li.xpath('.//span[@class="has--icon count--download"]/text()').extract_first()
			download = re.sub(r',', '', download)

			# 更新时间，Unix时间戳
			date_update = li.xpath('.//span[@class="has--icon date--updated"]/abbr/text()').extract_first()
			unix_update = li.xpath('.//span[@class="has--icon date--updated"]/abbr/@data-epoch').extract_first()
			
			# 上传时间，Unix时间戳
			date_upload = li.xpath('.//span[@class="has--icon date--created"]/abbr/text()').extract_first()
			unix_upload = li.xpath('.//span[@class="has--icon date--created"]/abbr/@data-epoch').extract_first()
			
			# mod简介，谷歌翻译
			info = li.xpath('.//div[@class="list-item__description"]/p/text()').extract_first()
			info_cn = trans.translate(info, dest='zh-cn').text
			
			# 链接，构造绝对URL
			href = li.xpath('.//div[@class="list-item__details xs-mg-r-1"]/a/@href').extract_first()
			link = response.urljoin(href)
			
			# 使用获取的数据生成字典
			yield{
			'name': name,
			'name_cn': name_cn,
			'category': category,
			'category_cn': category_cn,
			'download': download,
			'date_update': date_update,
			'unix_update': unix_update,
			'date_upload': date_upload,
			'unix_upload': unix_upload,
			'info': info,
			'info_cn': info_cn,
			'link': link,
			}
		
		# 获取下一页链接并持续爬取
		next_url = response.xpath('//a[@rel="next"]/@href').extract_first()
		if next_url is not None:
			next_url = response.urljoin(url=next_url)
			yield scrapy.Request(next_url, callback=self.parse)
