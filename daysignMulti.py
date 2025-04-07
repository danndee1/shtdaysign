import os
import re
import time
import httpx
import traceback
import random
import math
from datetime import datetime, timedelta  # 正确导入 datetime 和 timedelta
from contextlib import contextmanager
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from flaresolverr import FlareSolverrHTTPClient

SEHUATANG_HOST = 'www.sehuatang.net'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

FID = 103  # 高清中文字幕

AUTO_REPLIES = (
    '感谢楼主分享好片',
    '感谢分享！！',
    '感谢分享感谢分享',
    '必需支持',
    '简直太爽了',
    '感谢分享啊',
    '封面还不错',
    '有点意思啊',
    '封面还不错，支持一波',
    '真不错啊',
    '不错不错',
    '这身材可以呀',
    '终于等到你',
    '不错。。！',
    '謝謝辛苦分享',
    '赏心悦目',
    '快乐无限~~',
    '這怎麼受的了啊',
    '谁也挡不住！',
    '感謝分享',
    '分享支持。',
    '这谁顶得住啊',
    '这是要精J人亡啊！',
    '饰演很赞',
    '這系列真有戲',
    '感谢大佬分享',
    '看着不错',
    '感谢老板分享',
    '可以看看',
    '谢谢分享！！！',
    '非常感谢！',
    '楼主威武！',
    '辛苦了，谢谢分享',
    '分享愉快',
    '好片，收藏了',
    '多谢分享',
    '期待更多好作品',
    '楼主给力',
    '很棒，支持一下',
    '好人一生平安',
    '膜拜大神',
    '非常棒的资源',
    '这片子真不错',
    '值得一看',
    '好东西，支持',
    '下载看看',
    '楼主辛苦了',
    '多谢楼主',
    '相当不错',
    '厉害了，感谢',
    '优秀的资源'
)


def daysign(
    cookies: dict,
    flaresolverr_url: str = None,
    flaresolverr_proxy: str = None,
    proxies: dict = None  # 新增的 proxies 参数，用于传入代理配置
) -> str:
   # 如果传入了代理，则输出使用的代理
    if proxies:
        print(f"Using proxy: {proxies}")
    else:
        print("No proxy configured.")

    with (FlareSolverrHTTPClient(url=flaresolverr_url,
                                 proxy=flaresolverr_proxy,
                                 cookies=cookies,
                                 http2=True)
          if flaresolverr_url else httpx.Client(cookies=cookies, http2=True, proxies=proxies)) as client:

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
        wait_time = random.randint(1, 3)
        print(f'在选择题目之前等待 {wait_time} 秒...')
        time.sleep(wait_time)
        # 随机等待

        with _request(method='get', url=f'https://{SEHUATANG_HOST}/forum.php?mod=forumdisplay&fid={FID}') as r:
            tids = re.findall(r"normalthread_(\d+)", r.text,
                              re.MULTILINE | re.IGNORECASE)
            tid = random.choice(tids)
            print(f'choose tid = {tid} to comment')

        # 随机等待
        wait_time = random.randint(1, 3)
        print(f'随机等待 {wait_time} 秒...')
        time.sleep(wait_time)
        # 随机等待

        with _request(method='get', url=f'https://{SEHUATANG_HOST}/forum.php?mod=viewthread&tid={tid}&extra=page%3D1') as r:
            soup = BeautifulSoup(r.text, 'html.parser')
            formhash = soup.find('input', {'name': 'formhash'})['value']

        message = random.choice(AUTO_REPLIES)

        # 随机等待
        wait_time = random.randint(1, 3)
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

        # 随机等待
        wait_time = random.randint(1, 3)
        print(f'随机等待 {wait_time} 秒...')
        time.sleep(wait_time)
        # 随机等待
        with _request(method='get', url=f'https://{SEHUATANG_HOST}/plugin.php?id=dd_sign&ac=sign&infloat=yes&handlekey=pc_click_ddsign&inajax=1&ajaxtarget=fwin_content_pc_click_ddsign') as r:
            soup = BeautifulSoup(r.text, 'xml')
            html = soup.find('root').string
            # extract argument values from signform
            root = BeautifulSoup(html, 'html.parser')
            id_hash = (root.find('span', id=re.compile(r'^secqaa_'))
                       ['id']).removeprefix('secqaa_')
            formhash = root.find('input', {'name': 'formhash'})['value']
            signtoken = root.find('input', {'name': 'signtoken'})['value']
            action = root.find('form', {'name': 'login'})['action']
            print(
                f'signform values: id_hash={id_hash}, formhash={formhash}, signtoken={signtoken}')
            print(f'action href: {action}')

        # GET: https://www.sehuatang.net/misc.php?mod=secqaa&action=update&idhash=qS0&0.2010053552105764
        with _request(method='get', url=f'https://{SEHUATANG_HOST}/misc.php?mod=secqaa&action=update&idhash={id_hash}&{round(random.random(), 16)}') as r:
            qes_rsl = re.findall(r"'(.*?) = \?'", r.text,
                                 re.MULTILINE | re.IGNORECASE)

            if not qes_rsl or not qes_rsl[0]:
                # 检查是否是重复签到
                if '重复签到' in r.text:
                    return '重复签到'
                raise Exception('invalid or empty question!')
            qes = qes_rsl[0]
            ans = eval(qes)
            print(f'verification question: {qes} = {ans}')
            assert type(ans) == int

        # 随机等待
        wait_time = random.randint(1, 3)
        print(f'随机等待 {wait_time} 秒...')
        time.sleep(wait_time)
        # 随机等待
        # POST: https://www.sehuatang.net/plugin.php?id=dd_sign&mod=sign&signsubmit=yes&signhash=LMAB9&inajax=1
        with _request(method='post', url=f'https://{SEHUATANG_HOST}/{action.lstrip("/")}&inajax=1',
                      data={'formhash': formhash,
                            'signtoken': signtoken,
                            'secqaahash': id_hash,
                            'secanswer': ans}) as r:
            if '签到成功' in r.text:
                output = f"签到成功\n\n"
                #获取个人账号名
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
                    output += f"用户名: {masked_username} \n"
                #获取金币等信息
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
                    output += f"🤼‍♂️用户组：{user_group} \n💰金币：{gold}\n🥇积分：{points}\n😍色币：{coins}\n🔥评分：{ratings}\n"
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
            elif '重复签到' in r.text:
                return '重复签到'
            elif '需要先登录' in r.text:
                return '需要先登录'
            else:
                return r.text

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
    results = []  # 用于存储所有签到结果

    # 遍历多个 FETCH_98TANG 环境变量
    fetch_index = 1
    while os.getenv(f'FETCH_98TANG_{fetch_index}'):
        # 获取 cookies
        cookies = retrieve_cookies_from_fetch(f'FETCH_98TANG_{fetch_index}')
        
        # 获取对应的代理
        proxy = os.getenv(f'DEAULT_PROXY_{fetch_index}', None)
        if proxy:
            proxies = {'http://': proxy, 'https://': proxy}
            print(f"Using proxy for FETCH_98TANG_{fetch_index}: {proxies}")
        else:
            proxies = None
            print(f"No proxy configured for FETCH_98TANG_{fetch_index}")

        try:
            # 执行签到，并传递代理信息
            raw_html = daysign(
                cookies=cookies,
                flaresolverr_url=os.getenv('FLARESOLVERR_URL'),
                flaresolverr_proxy=os.getenv('FLARESOLVERR_PROXY'),
                proxies=proxies  # 将代理传递给 daysign 函数
            )

            if '签到成功' in raw_html:
                title = f'第{fetch_index}个账号'
                message_text = raw_html
            elif raw_html == '重复签到':
                title = f'第{fetch_index}个账号'
                message_text = '本日已签到，请勿重复签到'
            elif raw_html == '需要先登录':
                title = f'第{fetch_index}个账号 签到异常'
                message_text = 'Cookie无效或已过期，请重新获取'
            else:
                title = f'第{fetch_index}个账号 签到异常'
                message_text = raw_html
        except Exception as e:
            title = f'第{fetch_index}个账号 签到异常'
            message_text = f'错误原因：{e}'
            traceback.print_exc()

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
    send('🗓98堂每日签到', full_message)

if __name__ == '__main__':
    main()
