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

## 通信

- [ ] HTTP GET
- [ ] HTTP POST
- [ ] 正向 WebSocket
- [x] 反向 WebSocket

## API

- [x] send_group_msg
- [x] send_private_msg
- [x] send_msg
- [x] get_group_info
- [x] get_group_list
- [x] delete_msg
- [ ] get_msg
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
- [ ] set_group_add_request
- [x] get_login_info
- [x] get_stranger_info
- [ ] get_friend_list
- [x] get_group_member_info
- [x] get_group_member_list
- [ ] get_group_honor_info
- [x] get_image

## 消息段
- [x] Text
- [x] Image
- [ ] Audio
- [ ] File
- [ ] At
- [ ] MarketFace
- [ ] Quote
