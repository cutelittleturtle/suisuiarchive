# [SNH48-杨冰怡的补档小站 v2/An Online Archive Site for SNH48-YangBingyi](http://suisui.stream) [![Build Status](https://travis-ci.org/cutelittleturtle/suisuiarchive.svg?branch=master)](https://travis-ci.org/cutelittleturtle/suisuiarchive)

SNH48杨冰怡的补档小站第二版（半自动更新）。本版本采用了全新设计，收录SNH48-杨冰怡相关信息。所有信息仅收录链接；本站不对链接内容的有效性、合法性负责，同时不涉及任何版权。

An Online Archive Site for SNH48-YangBingyi (Semi-automatic update). The site contains information on performance, video streaming, video cuts that are performed by or partly by SNH48-YangBingyi. This site only contains hyperlinks to those contents, thus is not responsible for them. This site contains no copyright materials either.

# 自动更新/Auto-update

本文档将自动更新如下类容。为了保证更新成功，请勿手动修改以下任何文件。

自动更新依据应援会书写的视频名称进行。如果命名习惯改变，更新将失败，请通知作者。

```
直播 -> /文章/直播模块/睡前半小时.txt

公演 -> /文章/补档模块/《命运的X号》公演cut

外务 -> /文章/外务模块/48狼人杀.txt

未整理 -> 上面三类意外的更新，将暂且放入/assets/未整理.txt (可手动修改)

最近更新时间 -> /文章/更新时间.txt
```



# 手动维护/Manual Maintenance：
1. 登陆Github/suisuiarchive
2. 进入【文章】文件夹
3. 选取可手动修改的文件进行`/文章/`目录下`直/播模块`，`补档模块`，`外务模块`里的非自动更新文本文件，或者`/文章/unit展示.txt`和`/文章/未整理.txt`。您可以:
   1. 添加条目
   2. ~~修改条目目录结构~~ (请勿修改目录结构，否则自动更新可能失败)
   3. 添加子目录:如果需要添加子目录，在目录名前加上一个`#`号即可 (目前仅支持2级目录)


*注意: 未列出的文本文件可能会被更新代码生成的文件覆盖，修改则无效。*

#### 条目格式
 ```
视频名称
视频网址（必须以http://或https://开头）
 ```

#### 目录结构格式
 ```
公演(目录名）

视频名称1
视频网址1

视频名称2
视频网址2

#《梦想的旗帜》公演(子目录名）

视频名称3
视频网址3.1
视频网址3.2

 ```
**注意：条目与条目，目录名与条目之间必须由空行分割**

**一个条目可以拥有多个视频网址，中间不能有空行**

## 现有补档模块
```
公演补档区

    公演.txt -> 收录公演cut, 按公演名分子目录。

    最新活动.txt -> 收录外务、团内活动，如有长期单项活动会单独列出一个子目录。

    粉丝视频.txt -> 不完全收录粉丝制作的视频, 按照合集、安利向视频和搞事向视频分组。

    参与MV.txt -> 收录参加拍摄的MV

    演讲感言.txt -> 收录讲话读信性质的单独cut

    团内荣誉.txt -> 总选、B50等选举性质的相关cut

    生日会.txt -> 参加的成员生日会

    其他.txt -> 任何不在上述分类的链接。目前收录网易云音乐的电台。
    
unit展示区

    收录精彩unit cut
    
直播目录区

    收录直播电台补档
```


> 更多问题，请对照 `文章`文件夹中的示例文档。
>
> 或联系微博[饿饿的土拨鼠](https://weibo.com/u/5973150647/)

网站由个人维护，因为时间有限，所以不保证最新消息。

如有关于网站建设的建议和意见，请联系微博[饿饿的土拨鼠](https://weibo.com/u/5973150647/)

# 版权:

网站模板：[NexT Documentation](http://theme-next.iissnan.com/)

图片内容: [SNH48-杨冰怡](https://weibo.com/u/5491331848), [SNH48](http://www.snh48.com/)

源代码: [MIT License](https://opensource.org/licenses/MIT)