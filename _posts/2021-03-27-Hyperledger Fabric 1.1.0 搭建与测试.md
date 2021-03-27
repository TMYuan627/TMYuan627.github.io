---
layout:     post
title:      Hyperledger Fabric 1.1.0 搭建与测试
subtitle:   "吐血踩坑经验总结"
date:       2021-03-27
author:     汤泡饭
header-img: img/post-bg-hacker.jpg
music-id: 454828886
catalog: true
tags:
    - 区块链
---

> 从去年底到现在一直在准备今年的竞赛作品，其中一个主力项目是基于Hyperledger Fabric联盟链框架的电子病历相关应用。在完成作品背景调研、需求分析以及设计工作后，目前团队在进行作品实现。所以开始研究在云服务器上搭建Fabric项目的基础环境。由于Fabric项目是一个非常新、年轻的开源框架，中文资料稀少，英文资料理解困难，因此在云服务器上完成环境搭建并跑通示例非常不容易。特写此文，作为工具查阅。

 *参考资料*
* 1、[*《Hyperledger Fabric开发实战——快速掌握区块链技术》（杨毅）*](http://product.dangdang.com/25291813.html)
* 2、[*快速搭建一个Fabric1.0环境*](https://blog.csdn.net/qq_20513027/article/details/83214782)
* 3、[*Hyperledger Fabric 例子e2e部署启动失败几个小问题*](https://blog.csdn.net/weixin_41190227/article/details/86600821)

## 0 服务器环境
一开始选用的是腾讯云服务器，但不知道咋回事，在很多步骤执行过程中总是失败或卡住，查询了非常多的解决办法都没能解决，因此最终换成阿里云服务器。腾讯和阿里的服务器都使用的是学生认证版的基础服务器，价格非常便宜，性能及配置作为一个参赛作品服务器绰绰有余。

服务器操作系统：Ubuntu Server 18.04 LTS（参考资料1中的环境是CentOS，本人更熟悉Ubuntu环境）

**注意**：云服务器一般已开启SSH远程登录功能，若你选择使用虚拟机进行环境搭建，请记得在安装操作系统时**勾选SSH**。

**使用SSH远程登录服务器/虚拟机**：```sudo ssh (用户名)@(IP地址)```

## 1 安装基础工具

### 1.1 更新源列表
```sudo apt-get update```

### 1.2 安装`git`（用于拉取仓库中的源码）
```sudo apt install git```

### 1.3 安装`cURL`（用于发起网络请求）
```sudo apt install curl```

### 1.4 安装`docker`相关依赖
```sudo apt-get -y install apt-transport-https ca-certificates curl software-properties-common```

### 1.5 安装`make`工具
```sudo apt-get install make```

### 1.6 安装`libltdl-dev`
```sudo apt-get install libtool libltdl-dev```

## 2 安装`docker`
> Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的镜像中，然后发布到任何流行的 Linux或Windows 机器上，也可以实现虚拟化。

### 2.1 `docker`的安装
Docker用于方便、快速布局Fabric所需运行环境，它被打包在「容器」中来安装与卸载。很多教程在这里提到需要安装特定版本的Docker，那经过我无数次的实验，不管是失败还是成功，与Docker版本都没有太大关系。因此，这里直接安装最新版Docker即可:

1、安装`GPG`证书
```curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo apt-key add -```

2、写入软件源信息
```sudo add-apt-repository "deb [arch=amd64] http://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"```

3、再次更新源列表
```sudo apt-get -y update```

4、安装
```sudo apt-get -y install docker-ce```

5、安装完之后，查看版本
```docker --version```

出现如下字样则安装成功：
```Docker version 18.09.7, build 2d0083d```

### 2.2 设置用户组
设置非root用户也能执行docker，需要将普通用户加入docker组：
```sudo usermod -aG docker (用户名)```

### 2.3 添加阿里云`Hub`镜像（加速镜像pull）
1、在[*阿里云容器镜像服务中心*](https://cr.console.aliyun.com/)注册并拿到一个镜像地址

2、修改docker配置
```sudo vim /etc/docker/daemon.json```

3、添加以下内容并保存
```
{
  "registry-mirrors": ["阿里云Hub镜像地址"]
}
```
4、生效配置并重启docker
```
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 3 安装`docker-compose`
> docker-compose是Docker官方的开源项目，使用python编写，实现上调用了Docker服务的API进行容器管理。其官方定义为为「定义和运行多个Docker容器的应用（Defining and running multi-container Docker applications）」

### 3.1 执行安装
```sudo apt install docker-compose```

### 3.2 安装完之后，查看版本
```docker-compose --version```

出现如下字样则安装成功：
```docker-compose version 1.8.0, build unknown```

### 3.3 允许其他用户执行`compose`相关命令
```sudo chmod +x /usr/share/doc/docker-compose```

## 4 安装Go
>  Hyperledger Fabric许多组件使用Go编写，因此要运行Fabric框架，必须首先安装Go环境。Go的版本不是越新越好，新版本会出现不兼容的情况，Fabric 1.1.x要求Go版本为go1.11.x。

### 4.1 使用wget下载Go安装包
```sudo wget https://dl.google.com/go/go1.11.11.linux-amd64.tar.gz```

### 4.2 解压至指定路径
```sudo tar -zxvf go1.11.11.linux-amd64.tar.gz -C /usr/local/```

### 4.3 配置环境变量
1、打开并编辑`/etc/profile`文件
```sudo vim /etc/profile```

2、在末尾添加以下内容
```
export PATH=$PATH:/usr/local/go/bin
export GOROOT=/usr/local/go
export GOPATH=$HOME/go
export PATH=$PATH:$HOME/go/bin
```

3、**使配置生效！！**
```source /etc/profile```

4、验证安装成功
```go version```

出现如下字样则安装成功：
```go version go1.11.11 linux/amd64```

## 5 拉取`Fabric`源码
### 5.1 建立项目目录
```mkdir -p ~/go/src/github.com/hyperledger```

### 5.2 进入项目目录
```cd ~/go/src/github.com/hyperledger```

### 5.3 `Git`下载源代码
```git clone https://github.com/hyperledger/fabric.git```

**注意**：若无反应或卡住，尝试以下方法：
1、加`sudo`：

```sudo git clone https://github.com/hyperledger/fabric.git```

2、将`https`改为`git`：
```git clone git://github.com/hyperledger/fabric.git```

3、检查云服务器安全组策略是否开放443端口（https），建议将端口全部开放！

4、如果能下载但龟速，将`github.com`域名换为国内镜像源`github.com.cnpmjs.org`或`git.sdut.me`。（我曾尝试过该方法，可以快速下载源码，但在下一步切换branch时会出错，不推荐）

### 5.4 切换branch
1、查看项目所有branch
```git branch -a```

2、**将分支切换为`v1.1.0`（重要！！）**
```git checkout v1.1.0```

## 6 Pull `docker`镜像
> 因为在之前步骤中已经配置了Docker的阿里云镜像地址，此步会很快。如果还出现卡，可能是配置完镜像地址后没有重启Docker服务，请返回相应步骤重新配置。将Fabric v1.1.0版本所需的Docker运行环境镜像pull到本地。

### 6.1 进入项目目录
```cd ~/go/src/github.com/hyperledger/fabric/examples/e2e_cli/```

### 6.2 下载镜像（注意版本号对应！）
```source download-dockerimages.sh -c x86_64-1.1.0 -f x86_64-1.1.0```

### 6.3 查看镜像列表
```docker images```

> 出现的结果是，本地镜像中已成功下载了`tools`、`peer`、`orderer`、`ca`、`ccenv`、`javaenv`的`v1.1.0`版本镜像并被打上`latest`的标签。仔细观察下载镜像过程，你会发现有几个镜像因为「找不到指定版本的镜像」而下载失败。因为这几个镜像没有`v1.1.0`版本，**需要手动下载并打标签！**这是最容易失败的地方！

### 6.4 手动补充镜像
```
docker pull hyperledger/fabric-couchdb:x86_64-0.4.6
docker pull hyperledger/fabric-baseos:x86_64-0.4.6
docker pull hyperledger/fabric-kafka:x86_64-0.4.6
docker pull hyperledger/fabric-zookeeper:x86_64-0.4.6
```

### 6.5 打上`latest`标签
```
docker tag hyperledger/fabric-couchdb:x86_64-0.4.6 docker.io/hyperledger/fabric-couchdb:latest
docker tag hyperledger/fabric-baseos:x86_64-0.4.6 docker.io/hyperledger/fabric-baseos:latest
docker tag hyperledger/fabric-kafka:x86_64-0.4.6 docker.io/hyperledger/fabric-kafka:latest
docker tag hyperledger/fabric-zookeeper:x86_64-0.4.6 docker.io/hyperledger/fabric-zookeeper:latest
```

### 6.6 检查镜像列表
```docker images```

仔细核对下图镜像列表与版本号，**必须保持一致！**不一致的将其删除，并手动补充、打标签！

![](https://z3.ax1x.com/2021/03/27/6zFdER.jpg)

## 7 启动`Fabric`网络
### 7.1 切换到e2e_cli项目
```cd ~/go/src/github.com/hyperledger/fabric/examples/e2e_cli```

### 7.2 启动网络
```sudo ./network_setup.sh up```

### 7.3 成功！
![](https://z3.ax1x.com/2021/03/27/6zAnkn.png)

## 8 可能出现的问题
按上述步骤精确执行后，若还是启动失败，则参考以下解决方案：
* https://yq.aliyun.com/articles/238940
* https://blog.csdn.net/apple12655/article/details/89739348

## 9 后记
其实在部署到云服务器上之前，我在本机虚拟机上已经将1.1.0版本和1.4.0版本部署成功（也经历了N多莫名其妙的报错问题），但是忘记记录部署过程，导致后来在腾讯云上部署时，出现了非常多的错误和bug。并且这个框架还不成熟，对运行、依赖环境的版本有很精准的要求，这就导致每一次部署失败后要重装服务器系统，回到最初的纯净环境。大概我看日志记录，重装了30多次系统吧。。。后来弄了两三天，还是配不成功，我又想到能否将本机虚拟机直接迁移到云服务器。

果真，腾讯云和阿里云都提供了系统远程迁移的工具。腾讯云提供了在线迁移和离线迁移两种方案。首先尝试的是在线迁移，需要将它提供的工具在源系统中导入并运行，可惜我买的服务器带宽只有1MB，根本没有速率，无奈直接中断（还导致了云服务器进程被意外中断，直接崩溃，无法重装和登录）。后来尝试离线迁移，需要使用VMWare将虚拟机系统制作成镜像并上传到腾讯云COS对象存储数据库中（腾讯可真会创收），我去年疫情已入手2年的腾讯COS对象存储，非常快的将系统镜像传到了云，然后开始离线迁移。大概半个小时左右，提示我迁移完成。可是还是出现了问题。。。首先是SSH远程无法登录、ping也ping不同，只能在腾讯云控制台中登录。登录后处于没有网卡的状态，我对Linux系统更深度的配置也不是很懂，无奈再次放弃。

当晚十一点过更换阿里云服务器。阿里云服务器也提供了服务器迁移功能，可更惨的是它只能迁移到ECS高性能服务器，而不能迁移到我购买的学生专用轻量级服务器上。而我们团队的「财务总监」表示经费不够再买一台ECS了，于是只得作罢。

调整崩了无数次的心态，开始在阿里云服务器上再次从头开始配置环境，于是将成功步骤记录在上文，供无数踩坑者参考！（服务器配成功后的第一件事是啥？当然是保存快照！便于以后配不成功时一键恢复！）