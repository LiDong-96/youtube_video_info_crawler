#-*-coding:utf-8-*-
# 作者：Li Dong
import time
import json
from urllib import request
from urllib import error
from lxml import etree


def token_next_substracter(url):
    """
    爬取一个Youtube博主所有发布的视频的json页面的url里的两个参数
    @param url: 该博主主页的url（选项卡要选中“视频”）
    @type url: str
    @return: 形如(Mytoken, NextContinuationParams)的元组
    @rtype: tuple
    """
    global headers
    rqo = request.Request(url, headers=headers)
    while(True):
        try:
            rp = request.urlopen(rqo).read().decode("utf-8")
            break;
        except (error.HTTPError, error.URLError, ConnectionRefusedError):
            pass
    # 前30个视频的信息直接就放在上面请求之后获得的静态HTML里，准确说把信息放在json里，json放在一个javascript里
    # 所以用xpath把js取出来以后，切割字符串获得里面的json部分
    html_dom = etree.HTML(rp)
    list_Script = html_dom.xpath("body/script/text()")
    # print(list_Script)
    KeyScript = list_Script[1]
    processed_KeyScript = KeyScript[len("	   window[\"ytInitialData\"] = "): KeyScript.find(";\n")]
    # 数据提取
    dict_KeyScript = json.loads(processed_KeyScript)
    # 结构复杂的json，不知道有没有高效的方法可以一下子找到到达某个内容的路径
    gridRenderer = dict_KeyScript["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][1]["tabRenderer"]["content"]['sectionListRenderer']['contents'][0]['itemSectionRenderer']["contents"][0]['gridRenderer']
    list_gridVideoRenderer = gridRenderer["items"]
    for item in list_gridVideoRenderer:
        gridVideoRenderer = item["gridVideoRenderer"]
        videoID = gridVideoRenderer["videoId"]
        title = gridVideoRenderer["title"]["simpleText"].replace(",", "|")
        publishedTime = gridVideoRenderer["publishedTimeText"]["simpleText"]
        ViewCount = gridVideoRenderer["viewCountText"]["simpleText"].replace(",", "")
        written_content = ",".join([videoID, title, publishedTime, ViewCount])
        with open("D:\\xxx.txt", "a", encoding="utf-8") as f:
            f.write(written_content)
            f.write("\n")
    dict_continuations = gridRenderer["continuations"][0]
    MyToken = dict_continuations["nextContinuationData"]["continuation"]
    NextContinuationParams = dict_continuations["nextContinuationData"]["clickTrackingParams"]
    return (MyToken, NextContinuationParams)


def youtube_crawler(tuple_info):
    """
    爬取一个Youtube博主所有发布的视频的ID、标题、发布时间和浏览数四项信息
    @param tuple_info: 形如(Mytoken, NextContinuationParams)的元组
    @type tuple_info: tuple
    @return: 形如(Mytoken, NextContinuationParams)的元组
    @rtype: tuple
    """
    global headers
    # 如果实参为空元组，直接返回，结束函数
    if tuple_info == ():
        return ()
    else:
        # 先从形参里把url里两个必须的参数取出来
        NextContinuationParams = tuple_info[1]
        MyToken = tuple_info[0]
        # 组装URL并发送请求
        json_url = "https://www.youtube.com/browse_ajax?ctoken=" + MyToken + "&continuation=" + MyToken + "&itct=" + NextContinuationParams
        rqo_json = request.Request(json_url, headers=headers)
        # 访问URL，获得json
        while (True):
            try:
                rp_json = request.urlopen(rqo_json).read().decode("utf-8")
                break;
            except (error.HTTPError, error.URLError, ConnectionRefusedError):
                pass
        # 数据提取
        list_rp = json.loads(rp_json)
        dict_params = list_rp[1]
        gridContinuation = dict_params["response"]["continuationContents"]["gridContinuation"]
        list_gridVideoRenderer = gridContinuation["items"]
        for item in list_gridVideoRenderer:
            gridVideoRenderer = item["gridVideoRenderer"]
            videoID = gridVideoRenderer["videoId"]
            title = gridVideoRenderer["title"]["simpleText"].replace(",", "|")
            publishedTime = gridVideoRenderer["publishedTimeText"]["simpleText"]
            ViewCount = gridVideoRenderer["viewCountText"]["simpleText"].replace(",", "")
            written_content = ",".join([videoID, title, publishedTime, ViewCount])
            with open("D:\\xxx.txt", "a", encoding="utf-8") as f:
                f.write(written_content)
                f.write("\n")
        # 如果到了视频的最后一页，返回的json中键不存在“continuations”，最后一页，当然不存在下一页的信息
        try:
            dict_continuations = gridContinuation["continuations"][0]
            MyToken = dict_continuations["nextContinuationData"]["continuation"]
            NextContinuationParams = dict_continuations["nextContinuationData"]["clickTrackingParams"]
            return (MyToken, NextContinuationParams)
        except KeyError:
            return ()


if __name__ == '__main__':
    start_time = time.time()
    print("start time:", time.ctime())
    url = "https://www.youtube.com/channel/XXXXXXXXXXXXXXXXXXX/videos"
    # 请求头里的其他可以不要，这四样内容一个都不能少
    # 并且，这个只是不登陆的时候使用的请求头；如果登陆了，下面的cookie会变复杂，而且还需要其他的项
    # 不登陆虽然请求头简单一点，但是如果某个中文视频有做好的英文翻译，它就默认传那个英文内容给你
    headers = {
        "User-Agent": "XXXXXX",
        "X-YouTube-Client-Name": "XXX",
        "X-YouTube-Client-Version": "XXXXX",
        "Cookie": "XXX"
    }
    tuple_info = token_next_substracter(url)
    # print(tuple_info)
    tuple_next_info = youtube_crawler(tuple_info)
    # print(tuple_next_info)
    while tuple_next_info != ():
        tuple_next_info = youtube_crawler(tuple_next_info)
        # print(tuple_next_info)
    ending_time = time.time()
    print("end time:", time.ctime())
    print("lasting time:", ending_time - start_time)


