<h1 align="center"><i>✨ Lagrange Python (OneBot 11) ✨ </i></h1>

<h3 align="center">基于 Lagrange-Python 的 OneBot 11 实现</h3>

<p align="center">
  <a href="https://github.com/howmanybots/onebot/blob/master/README.md">
    <img src="https://img.shields.io/badge/OneBot-v11-blue?style=flat&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABABAMAAABYR2ztAAAAIVBMVEUAAAAAAAADAwMHBwceHh4UFBQNDQ0ZGRkoKCgvLy8iIiLWSdWYAAAAAXRSTlMAQObYZgAAAQVJREFUSMftlM0RgjAQhV+0ATYK6i1Xb+iMd0qgBEqgBEuwBOxU2QDKsjvojQPvkJ/ZL5sXkgWrFirK4MibYUdE3OR2nEpuKz1/q8CdNxNQgthZCXYVLjyoDQftaKuniHHWRnPh2GCUetR2/9HsMAXyUT4/3UHwtQT2AggSCGKeSAsFnxBIOuAggdh3AKTL7pDuCyABcMb0aQP7aM4AnAbc/wHwA5D2wDHTTe56gIIOUA/4YYV2e1sg713PXdZJAuncdZMAGkAukU9OAn40O849+0ornPwT93rphWF0mgAbauUrEOthlX8Zu7P5A6kZyKCJy75hhw1Mgr9RAUvX7A3csGqZegEdniCx30c3agAAAABJRU5ErkJggg==" alt="lgrpyob">
  </a>
</p>

## 简介

基于`Lagrange-Python`的`OneBot 11`实现，欢迎[提出Issue](https://github.com/HornCopper/Lagrange-Python.OneBot/issues)或[提出Pull Request](https://github.com/HornCopper/Lagrange-Python.OneBot/pulls)。

**本项目还不完善，如果想要用于生产环境，请移步[go-cqhttp(LagrangeGo)](https://github.com/LagrangeDev/go-cqhttp)或[Lagrange.Core](https://github.com/LagrangeDev/Lagrange.Core)。**

## 部署

~~破产~~省流版：`pip install pdm && pdm install && python __init__.py`。

然后会生成一个`config.yml`，按注释填完再运行`python __init__.py`，完事！

## 通信

- [x] HTTP GET
- [x] HTTP POST
- [x] 正向 WebSocket
- [x] 反向 WebSocket

## API

- [x] send_group_msg
- [x] send_private_msg
- [x] send_msg
- [x] get_group_info
- [x] get_group_list
- [x] delete_msg (Group Only)
- [x] get_msg
- [ ] get_forward_msg
- [ ] send_like
- [x] set_group_kick
- [x] set_group_ban
- [ ] set_group_anonymous_ban
- [x] set_group_whole_ban
- [ ] set_group_admin
- [ ] set_group_anonymous
- [x] set_group_card
- [x] set_group_name
- [x] set_group_leave
- [ ] set_group_special_title
- [ ] set_friend_add_request
- [x] set_group_add_request
- [x] get_login_info
- [x] get_stranger_info
- [x] get_friend_list
- [x] get_group_member_info
- [x] get_group_member_list
- [ ] get_group_honor_info
- [x] get_image
- [x] get_cookies

## 消息段
- [x] Text
- [x] Image
- [x] Audio
- [ ] File
- [x] At
- [ ] MarketFace
- [x] Quote (Receive Only)

## 事件

### 消息事件

- [x] PrivateMessage
- [x] GroupMessage

### 通知事件

- [ ] GroupUpload
- [x] GroupAdmin
- [x] GroupDecrease
- [x] GroupIncrease (Bad Support)
- [x] GroupBan
- [x] FriendAdd
- [x] GroupRecall
- [x] FriendRecall
- [x] FriendDeleted (Extension)
- [x] PokeNotify
- [ ] LuckyKingNotify
- [ ] HonorNotify

### 请求事件

- [x] FriendRequest
- [x] GroupRequest

## 注意

* 初次使用会生成`config.yml`位于项目根目录，**不要修改`config_template.yml`！！！**
* 按配置项填写完毕后再运行`python __init__.py`。
* 你需要自行解决`Sign Server`，本项目（基于`Lagrange-Python`）的`Sign Server`目前与`LagrangeDev`组织下的所有`Lagrange`项目的`Sign Server`均可以互通使用。
* [SignServer 自建教程](https://weibo.com/1687422352/5080257344832256)（大嘘）。

<details>
<summary>看到我了吗</summary

引用自`wyapx/README.md`

~~**还不快把star和follow给我交了**~~  

不然我就呜呜呜了  
![555](https://raw.githubusercontent.com/iceBear67/wyapx/dev/photo_2023-09-01_14-54-47.jpg)
</details>

## 贡献者

### Largange-Python.OneBot

[![][contrib-image_lgrpyob]][contrib-link_lgrpyob]

### Lagrange-Python(Pure Protocol)

[![][contrib-image_lgrpy]][contrib-link_lgrpy]

[contrib-image_lgrpy]: https://contrib.rocks/image?repo=LagrangeDev/lagrange-python

[contrib-link_lgrpy]: https://github.com/LagrangeDev/lagrange-python/graphs/contributors

[contrib-image_lgrpyob]: https://contrib.rocks/image?repo=HornCopper/Lagrange-Python.OneBot

[contrib-link_lgrpyob]: https://github.com/HornCopper/Lagrange-Python.OneBot/graphs/contributors
