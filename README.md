# ItemManagerWebsite
爱特工作室物品管理及财务管理系统

爱特工作室物品管理及财务管理系统是中国海洋大学爱特工作室开发的一个用于管理物品和财务的系统。该系统旨在帮助工作室更高效地管理物品库存和财务记录。遵循**MIT协议**开源，允许自由、合法地使用。

![ITSTUDIO](it-org.svg)

注：以下安装教程使用环境均为 Debian12 *(应该也不会有人用 Windows 部署这个吧)*

# 需要准备的软件包

使用系统的包管理器安装(如 apt, yum 等)

- git
- nodejs
- python3
- wget

# 前端

前端使用 Vue 框架开发，使用方法如下

## 安装

pnpm 包管理器安装：

```
wget -qO- https://get.pnpm.io/install.sh | sh -
```

```
pnpm install
```

### 启动服务
```
pnpm run serve
```

### 编译
```
pnpm run build
```

# 后端

后端使用 Django 框架开发，搭配 asgi + uvicorn + gunicorn 食用，运行`src/backend/start.sh`即可自动构建部署

若 venv 环境创建失败，请手动输入

```shell
apt install python3.x-venv # 其实就是安装 venv 包，x 是你的 python3 的小版本号
```

并且注意，在第一次启动前，需要在 `src/backend/item_manager` 中手动创建 secure.json 并将 `SECRET_KEY` 和 `SMTP` 填入，否则无法启动