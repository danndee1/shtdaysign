import os
import re
import time
import httpx
import traceback
import random
import math
import configparser
from datetime import datetime, timedelta
from contextlib import contextmanager
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from flaresolverr import FlareSolverrHTTPClient

# 加载配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 获取代理池配置
proxy_pool = [proxy.strip() for proxy in config.get('proxy_pool', 'proxies').split('\n') if proxy.strip()]
max_retries = config.getint('retry', 'max_retries')
retry_delay = config.getint('retry', 'retry_delay')

SEHUATANG_HOST = 'www.sehuatang.net'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

FID = 103  # 高清中文字幕

AUTO_REPLIES = (
    '这身材有点意思',
    '胸部看着挺不错',
    '封面让人心动啊',
    '低调支持一下吧',
    '画面有点小撩人',
    '这片子值得一瞧',
    '封面设计很用心',
    '暗戳戳地挺带感',
    '这资源有点味道',
    '看着心情还不错',
    '身材确实挺在线',
    '默默点个赞先',
    '这细节让人上头',
    '赏心悦目就够了',
    '内心已被点燃了',
    '这谁能不心动呢',
    '克制不住想看了',
    '支持一下很合理',
    '真挺不错低调爱',
    '这画面有点顶啊',
    '心里已经收藏了',
    '演技让人有点迷',
    '这系列暗藏惊喜',
    '胸部曲线挺勾人',
    '看着感觉还行吧',
    '先收藏再说别的',
    '内心波澜已起伏',
    '楼主懂我心意啊',
    '作品有点小精致',
    '看片心情很微妙',
    '好片得慢慢品味',
    '期待下次更精彩',
    '楼主暗藏功力深',
    '默默支持很可以',
    '好人自有好资源',
    '大神低调又给力',
    '资源看着很舒服',
    '这片子有点味道',
    '值得静静欣赏下',
    '好东西得细细看',
    '先下载品一品吧',
    '楼主真是藏龙啊',
    '感觉挺不错就行',
    '厉害了我的心动',
    '资源有点小惊喜',
    '绝了得慢慢感受',
    '这画面有点上瘾',
    '身材让人暗自赞',
    '封面已戳中我心',
    '内心已被彻底燃',
    '画面美得有点晕',
    '点赞得低调进行',
    '这片看着有内涵',
    '颜值暗暗在线啊',
    '手法有点小巧妙',
    '好看得不动声色',
    '谁看谁暗自喜欢',
    '完美得有点过分',
    '心动藏在眼神里',
    '收藏得不动声色',
    '身材让人暗挑眉',
    '这手法有点会啊',
    '画面感有点满分',
    '爱了得藏心里头',
    '这感觉有点上头',
    '完全暗戳戳喜欢',
    '支持得有点含蓄',
    '看了还想偷偷看',
    '这片子有点韵味',
        '这身材真绝了',
    '奶子真是棒极了',
    '胸部简直完美啊',
    '必须大力支持呀',
    '看着就爽到飞起',
    '这片子绝对给力',
    '封面美得冒泡了',
    '真是有点小刺激',
    '封面赞爆支持一波',
    '实在是太棒了吧',
    '不错不错爱了爱了',
    '身材火辣顶不住啊',
    '终于等到好货了',
    '这资源看着带劲',
    '画面赏心悦目啊',
    '快乐简直停不下来',
    '这谁能扛得住啊',
    '完全无法抵挡住',
    '支持大佬冲冲冲',
    '真心不错爱死了',
    '谁看了不心动啊',
    '简直让人把持不住',
    '演技在线太会了',
    '这系列越来越有料',
    '胸部好看顶呱呱',
    '看着就觉得带感',
    '完全可以冲一冲',
    '已经果断收藏了',
    '楼主真是威武霸气',
    '作品精彩顶不住',
    '看片心情超愉快',
    '好片必须收藏啊',
    '期待更多精彩内容',
    '楼主给力顶顶顶',
    '超棒必须支持下',
    '好人一生平安呐',
    '膜拜大神太牛了',
    '资源优秀爱疯了',
    '这片子真心够味',
    '绝对值得一看啊',
    '好东西必须支持',
    '赶紧下载来欣赏',
    '楼主牛逼闪闪发光',
    '相当不错爱了爱了',
    '大佬厉害顶起来',
    '资源绝赞冲冲冲',
    '绝了必须疯狂爱',
    '这也太顶了吧唧',
    '身材完美绝绝子',
    '封面杀得我心动',
    '完全顶不住诱惑',
    '画面美到炸裂了',
    '必须疯狂点赞啊',
    '这片有看头带劲',
    '颜值在线顶不住',
    '太会撩人了吧唧',
    '好看到直接炸了',
    '谁看了不爱疯啊',
    '完美到让人窒息',
    '瞬间心动收藏了',
    '直接果断收藏了',
    '身材绝了顶不住',
    '真会玩我心动了',
    '画面感满分赞爆',
    '爱了爱了停不下',
    '这也太赞了兄弟',
    '完全戳中我心巴',
    '必须支持一波走起',
    '看了还想再看啊',
    '这片够味真带感',
)

def get_random_proxy():
    """从代理池中随机获取一个代理"""
    if not proxy_pool:
        return None
    return random.choice(proxy_pool)

def create_proxy_dict(proxy_url):
    """创建代理字典"""
    if not proxy_url:
        return None
    return {
        'http': proxy_url,
        'https': proxy_url
    }

def daysign(
    cookies: dict,
    flaresolverr_url: str = None,
    flaresolverr_proxy: str = None,
    proxies: dict = None  # 新增的 proxies 参数，用于传入代理配置
) -> str:
    current_proxy = None
    used_proxies = set()  # 记录已使用的代理
    
    # 如果传入了代理，则使用环境变量代理
    if proxies:
        print(f"使用环境变量代理: {proxies}")
        current_proxy = proxies
    else:
        # 从代理池中随机选择一个代理
        proxy_url = get_random_proxy()
        if proxy_url:
            current_proxy = create_proxy_dict(proxy_url)
            print(f"使用代理池代理: {current_proxy}")
            used_proxies.add(proxy_url)

    for retry in range(max_retries):
        try:
            client = (FlareSolverrHTTPClient(url=flaresolverr_url,
                                     proxy=flaresolverr_proxy,
                                     cookies=cookies,
                                     http2=True)
                if flaresolverr_url else httpx.Client(cookies=cookies, http2=True, proxies=current_proxy))

            @contextmanager
            def _request(method, url, *args, **kwargs):
                r = client.request(method=method, url=url,
                                   headers={
                                       'user-agent': DEFAULT_USER_AGENT,
                                       'x-requested-with': 'XMLHttpRequest',
                                       'dnt': '1',
                                       'accept': '*/*',
                                       'sec-ch-ua-mobile': '?0',
                                       'sec-ch-ua-platform': 'macOS',
                                       'sec-fetch-site': 'same-origin',
                                       'sec-fetch-mode': 'cors',
                                       'sec-fetch-dest': 'empty',
                                       'referer': f'https://{SEHUATANG_HOST}/plugin.php?id=dd_sign&mod=sign',
                                       'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                                   }, *args, **kwargs)
                try:
                    r.raise_for_status()
                    yield r
                finally:
                    r.close()

            with client:
                age_confirmed = False
                age_retry_cnt = 3
                while not age_confirmed and age_retry_cnt > 0:
                    with _request(method='get', url=f'https://{SEHUATANG_HOST}/') as r:
                        if (v := re.findall(r"safeid='(\w+)'",
                                            r.text, re.MULTILINE | re.IGNORECASE)) and (safeid := v[0]):
                            print(f'set age confirm cookie: _safe={safeid}')
                            client.cookies.set(name='_safe', value=safeid)
                        else:
                            age_confirmed = True
                        age_retry_cnt -= 1

                if not age_confirmed:
                    raise Exception('failed to pass age confirmation')

                # 随机等待
                wait_time = random.randint(4, 10)
                print(f'在选择题目之前等待 {wait_time} 秒...')
                time.sleep(wait_time)
                # 随机等待

                with _request(method='get', url=f'https://{SEHUATANG_HOST}/forum.php?mod=forumdisplay&fid={FID}') as r:
                    tids = re.findall(r"normalthread_(\d+)", r.text,
                                      re.MULTILINE | re.IGNORECASE)
                    tid = random.choice(tids)
                    print(f'choose tid = {tid} to comment')

                # 随机等待
                wait_time = random.randint(4, 10)
                print(f'随机等待 {wait_time} 秒...')
                time.sleep(wait_time)
                # 随机等待

                with _request(method='get', url=f'https://{SEHUATANG_HOST}/forum.php?mod=viewthread&tid={tid}&extra=page%3D1') as r:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    formhash = soup.find('input', {'name': 'formhash'})['value']

                message = random.choice(AUTO_REPLIES)

                # 随机等待
                wait_time = random.randint(3, 10)
                print(f'随机等待 {wait_time} 秒...')
                time.sleep(wait_time)
                # 随机等待
                with _request(method='post', url=f'https://{SEHUATANG_HOST}/forum.php?mod=post&action=reply&fid={FID}&tid={tid}&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1',
                              data={
                                  'file': '',
                                  'message': message,
                                  'posttime': int(time.time()),
                                  'formhash': formhash,
                                  'usesig': '',
                                  'subject': '',
                              }) as r:
                    print(f'comment to: tid = {tid}, message = {message}')

                with _request(method='get', url=f'https://{SEHUATANG_HOST}/plugin.php?id=dd_sign&mod=sign') as r:
                    # id_hash_rsl = re.findall(
                    #     r"updatesecqaa\('(.*?)'", r.text, re.MULTILINE | re.IGNORECASE)
                    # id_hash = id_hash_rsl[0] if id_hash_rsl else 'qS0'  # default value

                    # soup = BeautifulSoup(r.text, 'html.parser')
                    # formhash = soup.find('input', {'name': 'formhash'})['value']
                    # signtoken = soup.find('input', {'name': 'signtoken'})['value']
                    # action = soup.find('form', {'name': 'login'})['action']
                    pass
                #获取个人账号名
                # 随机等待
                wait_time = random.randint(1, 3)
                print(f'随机等待 {wait_time} 秒...')
                time.sleep(wait_time)
                # 随机等待
                with _request(method='get', url=f'https://{SEHUATANG_HOST}/home.php?mod=spacecp&ac=profile') as r:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    
                    # 查找标签
                    username_element = soup.find('strong', class_='vwmy')

                    # 提取用户信息
                    if username_element:
                        username = username_element.text
                        # 掩码处理：保留首字母和最后一字母，其他部分用星号代替
                        def mask_username(username):
                            if len(username) <= 2:
                                # 如果用户名只有一两位，掩码一半或完全掩盖
                                return username[0] + '*' * (len(username) - 1)
                            else:
                                return username[0] + '*' * (len(username) - 2) + username[-1]

                        masked_username = mask_username(username)
                        print(f"用户名: {masked_username}")
                    else:
                        print("未找到用户名")

                    # 输出结果
                    output = f"🙋‍♂️用户名: {masked_username} \n"
                #获取金币等信息
                # 随机等待
                wait_time = random.randint(1, 3)
                print(f'随机等待 {wait_time} 秒...')
                time.sleep(wait_time)
                # 随机等待
                with _request(method='get', url=f'https://{SEHUATANG_HOST}/home.php?mod=spacecp&ac=credit&showcredit=1') as r:
                    soup = BeautifulSoup(r.text, 'html.parser')
                   
                    # 查找所有带有 <li> 标签的积分信息

                    credit_info = soup.find_all('li')

                    # 提取积分和金钱等信息
                    credits = {}
                    first_integral_found = False
                    for item in credit_info:
                        if item.find('em'):  # 检查是否有 <em> 标签
                            key = item.find('em').text.strip().replace(':', '')
                            value = item.text.split(":")[-1].strip()
                            if key == "积分" and not first_integral_found:
                                credits[key] = value
                                first_integral_found = True
                            elif key!= "积分":
                                credits[key] = value

                    # 获取用户组信息
                    user_group_tag = soup.find('a', {'id': 'g_upmine'})
                    user_group = user_group_tag.text.split(":")[-1].strip() if user_group_tag else '未找到'

                    # 获取各类积分信息，并进行输出格式化
                    gold = credits.get('金钱', '未找到')
                    points = credits.get('积分', '未找到')
                    coins = credits.get('色币', '未找到')
                    ratings = credits.get('评分', '未找到')

                    # 输出结果
                    output += f"🤼‍♂️用户组：{user_group} \n💰金币：{gold}\n💯积分：{points}\n😍色币：{coins}\n🔥评分：{ratings}\n"
                #获取升级详情
                # 随机等待
                wait_time = random.randint(1, 3)
                print(f'随机等待 {wait_time} 秒...')
                time.sleep(wait_time)
                # 随机等待
                with _request(method='get', url=f'https://{SEHUATANG_HOST}/home.php?mod=spacecp&ac=usergroup') as r:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    # 获取晋级用户组信息
                    upgrade_usergroup = soup.find('li', {'id': 'c2'}).text
                    #print("晋级用户组信息:", upgrade_usergroup)

                    # 查找包含晋级用户组信息的div
                    tscr_div = soup.find('div', class_='tscr')

                    if tscr_div:
                        # 提取升级所需积分信息
                        required_points = tscr_div.find('span', class_='notice').text
                        # 从文本中提取积分数字
                        points_needed = int(required_points.split('积分')[1].strip())

                        # 计算预计升级时间
                        points_per_day = 3
                        days_needed = points_needed / points_per_day

                        # 手动向上取整
                        if days_needed != int(days_needed):
                            days_needed_ceil = int(days_needed) + 1
                        else:
                            days_needed_ceil = int(days_needed)

                        # 计算预计升级日期
                        today = datetime.now()
                        todayDate = today.date()  
                        upgrade_date = todayDate + timedelta(days=days_needed_ceil)
                    else:
                        print("未找到包含晋级用户组信息的 div。")

                    # 输出结果
                    output += f"\n{upgrade_usergroup} \n{required_points}\n"
                    output += f"预计还需{days_needed_ceil}天\n"
                    output += f"预计升级时间: {upgrade_date}"
                return output

        except httpx.ProxyError as e:
            print(f"代理错误: {str(e)}")
            if current_proxy:
                print(f"当前代理 {current_proxy} 不可用，尝试切换代理...")
                # 尝试使用新的代理
                available_proxies = [p for p in proxy_pool if p not in used_proxies]
                if available_proxies:
                    proxy_url = random.choice(available_proxies)
                    current_proxy = create_proxy_dict(proxy_url)
                    used_proxies.add(proxy_url)
                    print(f"切换到新代理: {current_proxy}")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("所有代理都已尝试过，无法继续")
                    raise Exception("所有代理都不可用")
            else:
                raise Exception(f"代理错误: {str(e)}")

        except httpx.RequestError as e:
            print(f"请求错误: {str(e)}")
            if retry < max_retries - 1:
                print(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                continue
            else:
                raise Exception(f"请求错误: {str(e)}")

        except Exception as e:
            print(f"未知错误: {str(e)}")
            traceback.print_exc()
            if retry < max_retries - 1:
                print(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                continue
            else:
                raise Exception(f"未知错误: {str(e)}")

def retrieve_cookies_from_curl(env: str) -> dict:
    cURL = os.getenv(env, '').replace('\\', ' ')
    try:
        import uncurl
        return uncurl.parse_context(curl_command=cURL).cookies
    except ImportError:
        print("uncurl is required.")


def retrieve_cookies_from_fetch(env: str) -> dict:
    def parse_fetch(s: str) -> dict:
        ans = {}
        exec(s, {
            'fetch': lambda _, o: ans.update(o),
            'null': None
        })
        return ans
    cookie_str = parse_fetch(os.getenv(env))['headers']['cookie']
    return dict(s.strip().split('=', maxsplit=1) for s in cookie_str.split(';'))


def preprocess_text(text) -> str:
    if 'xml' not in text:
        return text

    try:
        root = ET.fromstring(text)
        cdata = root.text
        soup = BeautifulSoup(cdata, 'html.parser')
        for script in soup.find_all('script'):
            script.decompose()
        return soup.get_text()
    except:
        return text


def push_notification(title: str, content: str) -> None:

    def telegram_send_message(text: str, chat_id: str, token: str, silent: bool = False) -> None:
        r = httpx.post(url=f'https://api.telegram.org/bot{token}/sendMessage',
                       json={
                           'chat_id': chat_id,
                           'text': text,
                           'disable_notification': silent,
                           'disable_web_page_preview': True,
                       })
        r.raise_for_status()

    try:
        from notify import telegram_bot
        telegram_bot(title, content)
    except ImportError:
        chat_id = os.getenv('TG_USER_ID')
        bot_token = os.getenv('TG_BOT_TOKEN')
        if chat_id and bot_token:
            telegram_send_message(f'{title}\n\n{content}', chat_id, bot_token)


def main():
    raw_html = None
    results = []  # 用于存储所有评论结果

    # 遍历多个 FETCH_98TANG 环境变量
    fetch_index = 1
    while os.getenv(f'FETCH_98TANG_{fetch_index}'):
        try:
            # 获取 cookies
            cookies = retrieve_cookies_from_fetch(f'FETCH_98TANG_{fetch_index}')
            
            # 获取对应的代理
            proxy = os.getenv(f'DEAULT_PROXY_{fetch_index}', None)
            if proxy:
                proxies = {'http': proxy, 'https': proxy}
                print(f"账号 {fetch_index} 使用环境变量代理: {proxies}")
            else:
                proxies = None
                # 移除错误提示，直接使用代理池
                print(f"账号 {fetch_index} 使用代理池")

            # 执行评论，并传递代理信息
            raw_html = daysign(
                cookies=cookies,
                flaresolverr_url=os.getenv('FLARESOLVERR_URL'),
                flaresolverr_proxy=os.getenv('FLARESOLVERR_PROXY'),
                proxies=proxies
            )

            if '积分' in raw_html:
                title = f'第{fetch_index}个账号 积分详情\n'
                message_text = raw_html
            else:
                title = f'第{fetch_index}个账号 评论异常'
                message_text = raw_html

        except Exception as e:
            title = f'第{fetch_index}个账号 评论异常'
            message_text = f'错误原因：{str(e)}\n详细错误信息：{traceback.format_exc()}'
            print(f"账号 {fetch_index} 评论失败: {message_text}")

        # 处理并保存结果
        message_text = preprocess_text(message_text)
        results.append(f'{title}\n{message_text}')
        
        fetch_index += 1

    # 输出所有结果
    for result in results:
        print(result)

    #青龙通知
    full_message = "\n\n".join(results)
    from notify import send
    send('🗓98堂评论', full_message)



if __name__ == '__main__':
    main()
