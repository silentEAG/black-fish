前言概述
====


KoiStealer是一种新型的窃密类木马，攻击者主要通过钓鱼邮件进行传播，该窃密木马能获取受害者屏幕截图、浏览器中储者的密码、Cookie等数据，然后利用盗取的这些数据，对受害者进行更进一步的诈骗攻击活动，笔者最近捕获到该木马最新的攻击活动，对该攻击活动攻击链样本进行了详细分析，供大家参考学习。


详细分析
====


1\.钓鱼样本解压缩之后，伪装成PDF图标的快捷方式，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191248-312fda58-2fbf-1.png)  

2\.快捷方式执行的命令行参数，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191303-3a0760e2-2fbf-1.png)  

3\.创建计划任务启动项，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191317-42ee1390-2fbf-1.png)  

4\.从远程服务器上下载计划任务启动项对应的恶意脚本文件并存放到%temp%目录下，下载的恶意脚本，从远程服务器上下载另外一个恶意脚本，并删除之前的计划任务启动项，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191332-4b8d9138-2fbf-1.png)  

5\.下载的恶意脚本，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191344-52997fe6-2fbf-1.png)  

6\.恶意脚本将自身拷贝到%ProgramData%目录下并重命名，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191357-5a9fc20e-2fbf-1.png)  

7\.从远程服务器上下载恶意PowerShell脚本并执行，恶意PowerShell脚本内容，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191409-61602200-2fbf-1.png)  

8\.恶意PowerShell脚本从远程服务器上请求PayLoad数据，PayLoad的编译时间为2024年2月21日，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191421-688d62d6-2fbf-1.png)  

9\.然后通过ShellCode在内存中加载执行PayLoad数据，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191434-7042839e-2fbf-1.png)  

10\.ShellCode加载器代码，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191446-776bff60-2fbf-1.png)  

11\.PayLoad代码，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191457-7e0e0ffc-2fbf-1.png)  

12\.获取程序资源数据，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191511-86a4e938-2fbf-1.png)  

13\.获取的资源数据ID为47574存储到分配的内存空间当中，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191526-8f9e39d6-2fbf-1.png)  

14\.获取的资源数据ID为37252存储到分配的内存空间当中，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191540-97cff28e-2fbf-1.png)  

15\.利用资源数据ID为37252的解密Key，解密资源数据ID为47574的加密数据，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191554-a0532d36-2fbf-1.png)  

16\.将加密的资源数据，拷贝到内存中，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191608-a88668c4-2fbf-1.png)  

17\.解密加密的资源数据，解密算法，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191620-afe0c3e4-2fbf-1.png)  

18\.解密之后的资源数据，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191634-b7f8d170-2fbf-1.png)  

19\.然后分配内存，将解密的PayLoad加载到该内存中，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191647-bfdb0e12-2fbf-1.png)  

20\.最后跳转执行到PayLoad代码入口点，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191700-c7c71cc4-2fbf-1.png)  

21\.解密之后的PayLoad编译时间为2024年6月4日，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191714-cfb5cc3c-2fbf-1.png)  

22\.PayLoad代码，会判断机器操作系统语言版本，如果为以下语言ID版本，则直接退出程序，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191730-d98d561c-2fbf-1.png)  

23\.获取主机相关信息，如果不满足，则退出程序，主要是为了反沙箱操作，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191744-e1a248bc-2fbf-1.png)  

24\.通过获取主机的文件信息，用户名等信息反沙箱，例如获取主机用户名，判断是否为列表中的用户名，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191757-e9be8650-2fbf-1.png)  

25\.获取远程服务器URL连接地址hxxp://176\.10\.111\[.]71/guapen.php， 并创建临时文件，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191821-f81ace02-2fbf-1.png)  

26\.获取%ProgramData%目录下的恶意脚本文件，并设置计划任务，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191852-0a3a8a64-2fc0-1.png)  

27\.设置的计划任务，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191906-12d966f4-2fc0-1.png)  

28\.从远程服务器上获取相应的配置文件数据，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191919-1a7d1e0a-2fc0-1.png)  

29\.通过固定的请求数据格式，向远程服务器发起请求，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191933-229e118e-2fc0-1.png)  

30\.请求数据格式内容，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191946-2a8d0bca-2fc0-1.png)  

31\.获取主机名等信息，然后以固定格式向远程服务器发送POST请求，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621191959-327abeae-2fc0-1.png)  

32\.从远程服务器下载恶意PowerShell脚本并执行，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192014-3b033a88-2fc0-1.png)  

33\.下载的恶意脚本，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192026-42446fce-2fc0-1.png)  

34\.从远程服务器上下载配置数据，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192038-49995096-2fc0-1.png)  

35\.恶意文件配置数据，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192051-5172eb1a-2fc0-1.png)  

36\.异或解密上面的加密数据，并加载执行，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192106-59ecef3e-2fc0-1.png)  

37\.解密出来的最后PayLoad是一个NET编写的程序，使用Obfuscar(1\.0\)\[\-]混淆，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192119-61df2e8c-2fc0-1.png)  

38\.解混淆之后，与此前分析的KoiStealer代码结构一致，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192134-6af403c6-2fc0-1.png)  

39\.获取到相关的配置信息，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192148-735081fc-2fc0-1.png)  

40\.获取浏览器相关信息，如下所示：  

![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192201-7b3c59c2-2fc0-1.png)


威胁情报
====


![](https://xzfile.aliyuncs.com/media/upload/picture/20240621192219-857274b2-2fc0-1.png)


总结结尾
====


黑客组织利用各种恶意软件进行的各种攻击活动已经无处不在，防不胜防，很多系统可能已经被感染了各种恶意软件，全球各地每天都在发生各种恶意软件攻击活动，黑客组织一直在持续更新自己的攻击样本以及攻击技术，不断有企业被攻击，这些黑客组织从来没有停止过攻击活动，而且非常活跃，新的恶意软件层出不穷，旧的恶意软件又不断更新，需要时刻警惕，可能一不小心就被安装了某个恶意软件。