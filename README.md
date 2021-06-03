# 语音控制机器人示例

使用控制设备通过Azero平台对任意可编程机器人实现语音控制指南（以树莓派六足机器人举例）

（关于此机器人的信息可以在[官网](https://www.hiwonder.com/product-detail/SpiderPi-Intelligent-Visual-Robot.html)上找到）

## 目录
* [项目原理及Azero平台介绍](#1)
* [机器人联网](#2)
* [设备技能和意图的背景资料](#3)
* [创建产品和对应的设备](#4)
* [配置一个专属技能](#5)
* [为设备添加技能](#6)
* [在树莓派中运行程序](#7)
* [树莓派如何开机自动运行所需文件](#8)
* [具体应用时的建议](#9)
* [语音控制](#10)
* [具体展示](#11)
----------
### 第一步：项目原理及Azero平台介绍（详细信息请见[白皮书](https://cms-azero.soundai.cn:8443/v1/cmsservice/resource/052416852598542c4e4291a885ac2152.pdf?showname=SoundAI_Azero%E7%99%BD%E7%9A%AE%E4%B9%A6v1.0)）<a id="1"> </a>

![](https://document-azero.soundai.com.cn/assets/img/image-1.b1ddbc56.png)

Azero系统结构主要分为三部分：即第三方、服务端、以及设备端。


	- 第三方是为了方便客户对产品功能进行扩展，主要分四类：
		- 某些产品需要此领域专有的NLP来完善功能；
		- 某些产品需要此领域专有的ASR来完善功能；
		- 产品有功能需要大型的私有部署的技能支持；
		- 需要对接一些独有的音频、视频、有声等内容。
	
本项目主要涉及设备端及服务端。



- 设备端：
	- 一个作为控制入口的设备（设备和设备接入详情可见第二步）
		- 可使用音箱、手机等带有麦克风的设备
		- 如想添加技能，[iOS](https://github.com/sai-azero/Azero-SDK-for-iOS)，[Linux](https://github.com/sai-azero/Azero_SDK_for_Linux)，[Android](https://github.com/sai-azero/Azero_SDK_for_Android)，[RTOS](https://github.com/sai-azero/Azero_SDK_for_RTOS)系统均有开源SDK可供下载
		- 试玩Azero基本功能可直接使用app
	- 一个被控制的IoT设备
		- 本项目中为树莓派六足机器人
- 服务端：
	- 控制设备的技能开发及部署（技能详情可见第二步）
		- 通过开发技能，用户可为设备设计专属功能
		- 通过部署技能（官方技能，第三方技能，自己的开发的技能），控制设备就像装了app的手机，可以实现特定的功能。
		- 本项目中技能为：向六足机器人发出控制信号

总结来说原理就是：通过控制设备输入音频-> 服务端分析音频并判断技能和意图 -> 传指令到IoT设备 -> IoT设备进行操作
 
----------
### 第二步：机器人联网（以树莓派六足机器人举例）<a id="2"> </a>
- 目的：确保机器人和发送指令的硬件连接到同一个局域网或手机热点，从而可以顺利向IoT设备发送指令
- 方法：
	1. 下载wonderPi软件（各大应用商城直接搜索）
	2. 选择局域网模式，并输入想要连接的局域网的密码
	3. 跟随指示连接机器人热点后返回app，静静等待即可
	4. 机器人下次开机便会自动连接




----------
### 第三步： 设备技能和意图的背景资料<a id="3"> </a>
目的：熟悉设备以及接入流程，熟悉技能以及意图。

方法：

- 设备接入的信息可在[GitHub](https://github.com/sai-azero/azero-devices-readme)或在官网设备接入[入门文档](http://document-azero.soundai.com.cn/device/docs/%E5%85%A5%E9%97%A8%E6%96%87%E6%A1%A3.html)中找到
- 技能的信息可在[GitHub](https://github.com/sai-azero/azero-skills-readme)或在官网[技能中心](http://document-azero.soundai.com.cn/skill/docs/)找到

----------
### 第四步：创建产品和对应的设备<a id="4"> </a>
目的：在开发者网站上将被控制的硬件注册成IoT设备

方法：

1. 注册并登陆[Azero IoT 开放平台](https://azero.soundai.com.cn/#/iot/home) 
	- IoT平台的简介可点击[了解详情](http://document-azero.soundai.com.cn/iot/docs/)进行查看
2. 选择[立即接入](https://azero.soundai.com.cn/iot/#/product-manage/product)并创建一个产品
	1. 填写产品信息并选择联网设备和WiFi
	2. 随后在下方设备管理中创建一个设备，选择创建证书并务必保存证书

----------
### 第五步： 配置一个专属技能<a id="5"> </a>
目的：创建一个独属于用户的技能，从而操控设备

方法：

1. 首先前往技能中心选择[立即接入](https://azero.soundai.com.cn/#/ask/createSkill)
- 创建技能时选择自定义任务型技能（开放）,并填写相关信息即可
- 关于意图的详细说明可以在[GitHub](https://github.com/sai-azero/azero-skills-readme)或在官网[技能中心](http://document-azero.soundai.com.cn/skill/docs/)找到，在此不再赘述
- 六足机器人的技能的意图配置为spiderman -> json.py 文件（包含意图：向后走，向前走，俯卧撑，右转，左转，示威，跺脚，扭动，向前扑，朋友再见，欢迎光临）
- 服务部署代码为 spiderman > 服务部署.py（line 54 和line 66 有两处需替换成用户专属的信息）
		
	**关于编写代码。 平台支持3种语言在线编辑，分别为Node.Js、Python、java。您也可以下载下方对应的SDK在本地开发调试再传到平台上在线部署使用。(此条只针对需代码开发的技能。)

		Node.Js SDK：https://github.com/sai-azero/azero-skills-kit-sdk-for-nodejs

		Python SDK：https://github.com/sai-azero/azero-skills-kit-sdk-for-python

		Java SDK：https://github.com/sai-azero/skill-sample-java-hello-world
- 完成代码并配置成功后就可以在右侧输入语料进行测试

----------
### 第六步：为设备添加技能<a id="6"> </a>
目的：赋予音箱或手机等控制设备控制IoT设备的能力

方法：

1. 前往[设备中心](https://azero.soundai.com.cn/#/avs/home)并创建设备，填入所需信息
- 在左侧技能配置中，添加自己刚刚创建的技能即可

----------
### 第七步：在树莓派中运行程序<a id="7"> </a>
目的：允许通过接收控制设备的信号从而控制机器人的动作

方法：

- [下载](https://www.realvnc.com/en/connect/download/viewer/windows/)VNC软件

	- VNC允许用户控制单个舵机，并自由组合动作，形成动作组
	- 具体连接方式可以参照用户手册第20页到第26页
	- 同时使用相同局域网而不是连接机器人的热点时，ip地址可通过手机app设备列表中长按蜘蛛图标得到

- [下载](https://mobaxterm.mobatek.net/download.html)MobaXterm
	- MobaXterm允许用户很简单的向树莓派中传送文件或从中复制文件达到备份的效果
	- ip地址得到方式和VNC中相同，specify username中填写pi

使用时，利用MobaXterm，用GitHub上的SpiderPiRobot替换树莓派中的Desktop/SpiderPiRobot.

----------

### 第八步：树莓派如何开机自动运行所需文件<a id="8"> </a>
目的：为了不必每次开机之后都需手动运行程序，自动运行后可直接开始对控制设备说话，发出指令


方法:



1. 在 /home/pi/.config 下创建一个文件夹，名称为 autostart，并在该文件夹下创建一个spider_start.desktop文件并修改Exec=/home/pi/Desktop/SpiderPiRobot/run.sh
2. 当前开机自动运行welcome.py，如需修改，修改/home/pi/Desktop/SpiderPiRobot/run.sh即可


----------
### 第九步： 具体应用时的建议<a id="9"> </a>
- SpiderPiRobot中，和json.py以及意图配置.py对应的是spiderman.py
- 使用时切记请将spiderman.py 中第11行的Host改为用户单独的IoT开放平台->设备管理->连接设备右侧查看按钮->交互中的API终端节点
- 如想添加新建的意图和对应的动作，只需在spiderman.py->line22->onetime_action 中添加
	- 冒号左侧为意图关联的PowerState，右侧为ActionGroups中的自创或原创动作组

- 使用VNC时自创动作组会被保存在hexapod的ActionGroups中，调用需要复制一份到Desktop内的ActionGroups中
- 将保存好的证书复制一份至SpiderPiRobot\python，并将line150：spiderman_pem 修改为证书文件夹的名字
- 将spiderman.py的line 39 替换为IoT开放平台 -> 设备管理->查看-> 交互-> 更新到此设备影子(最后一词update替换为#）

----------

### 第十步： 语音控制<a id="10"> </a>
	


1. 根据使用的设备，下载相应的SDK：[iOS](https://github.com/sai-azero/Azero-SDK-for-iOS)，[Linux](https://github.com/sai-azero/Azero_SDK_for_Linux)，[Android](https://github.com/sai-azero/Azero_SDK_for_Android)，[RTOS](https://github.com/sai-azero/Azero_SDK_for_RTOS)，并按照说明配置
	1. 此时设备正式成为控制设备
  
- Azero系统对语音做语音识别处理  
- 再经过nlp处理，匹配相应的技能，解析出意图和槽位（如果定义的有槽位）
- 机器人为端设备，iot中心与机器人的通信使用mqtt服务，机器人接收到消息后解析出相关控制指令，并依据指令做出相应操作


- 举例
	1. 说话人对麦克风说**往前走三步**，语音经过设备发送至Azero系统进行处理
	2. Azero系统对语音解析后匹配到在技能中心定义的机器人技能，触发前进意图，并获取到步数槽位信息“3”，意图的处理逻辑为向iot中心发送前进指令forward和步数信息“3”
	3. 机器人从iot中心获取到了forward和步数信息“3”，进而执行向前走动作三次。

----------


### 具体展示<a id="11"> </a>


- 视频为语音控制机器人运行动作组的演示视频（人形机器人的代码为TonyPi）
- 视频标题分别对应Desktop > SpiderPiRobot > python > welcome.py 中的continuous_action 和 onetime_action
- 语音指令可替换为其他可以表达相同意思的话，具体参照json.py中的每一意图对应的content
	- 语音控制和动作组文件一一对应，其中结尾为.d6a 为可以拼接或删除的动作组，.hwax 则为加密无法修改的预设动作组
- 动作组路径：Desktop > SpiderPiRobot > ActionGroups

**onetime_action:**



1. 表演舞蹈:"dance" 对应 duanwudao.d6a
2. 打个招呼:"welcome" 对应 say_hi.d6a
3. 健身："exercise" 对应 pushup.d6a
4. 再见："seeyou" 对应 wave_hand.d6a
5. 左转/右转："turn_left"/"turn_right"对应 3.d6a 和 4.d6a.
6. 武术 ："wushu" 对应 wushu.d6a

**continuous_action: (向前/向后走N步）**



1. 向前走: "forward" 对应 1.hwax
2. 向后退: "backward" 对应 2.hwax

*切记"dance"，"welcome"等名称需和AZERO平台中技能意图所关联的powerState相同


