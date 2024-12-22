<h2 align="center">社交网络挖掘期末项目</h2>

> [!CAUTION]
> - 每个小组对其实践项目成果在第 18 周之前（2025.01.02）向全班同学进行现场演示，做相关的介绍   
> - 分值：同学互评评分占 50%，教师和助教的评分占 30%，项目报告评分（教师和助教评判）占 20%   
> - 以书面报告（word 或 pdf 格式）的形式详细阐述本小组完成项目课题的基本思路、数据处理方式、算法、实现工具/语言、实验效果、性能评价和小组成员的分工说明（必需）等内容。报告可用中文或英文书写，要求不超过 8 页 A4 的篇幅


### 选题

<details>
<summary> 社交网络节点分析与社区挖掘 </summary>

- a. 应用某种社区挖掘算法划分网络中的不同社区，并用可视化技术展现出（具体展示工具不做硬性要求）。
- b. 对网络做进一步分析，例如应用各种节点的中心性度量算法将最具影响力/权威性/中枢性的节点识别并凸显出来，通过图、表等形式展现网络的各种属性度量结果（如节点间平均距离、度分布、图/社区的直径、网络结构演化等）。
- c. 附加任务（非必做，可任选其一）：
  - 链接预测：利用网络数据集提供的信息，设计一种机器学习模型预测网络中边的形成，同时说明预测模型性能评价的方法和结果。针对不同网络数据集，链接预测可对应不同的应用任务，如好友预测、科研合作预测、购买行为预测等。
  - 节点分类：设计一种模型判别网络中各节点的类别，同时说明模型性能评价的方法和结果。根据实际数据集可以实现二分类或多分类。

</details>


### 任务

- 具体任务
  - Preprocess
    - 存在同名作者，数据会累加
    - 存在大量单独（isolated）的点，在具体任务中应排除
  - Community Mining
    - 社区划分方法 参考PPT第六章：社区挖掘
    - 社区划分效果评价 参考PPT第八章：影响力和同质性 模块度内容
  - Centrality and other statistics
    - 中心性度量 参考PPT第三章：网络度量
    - 其他统计数据（度分布、聚类系数、平均路径长度等） 参考PPT第四章：网络模型
  - Link Prediction or Node Classification
- 细分任务
  - [x] 对数据集进行并行化预处理，抽取需要的信息并分块
  - [x] 对数据集的总体情况进行分析，并通过图表的形式进行展示
  - [ ] 寻找算法对论文进行分类，挖掘其论文类别社区，并进行可视化
  > 在总体图中仅可视化大于某个阈值的论文，点击进入具体类别后可视化该领域的所有论文，并更新对应的统计图
  - [ ] 对于挖掘出的不同类别社区，可视化其随时间的变化过程，挖掘不同时期的热门研究方向，挖掘该领域具有代表性的论文，并与真实情况做对比
  - [ ] 对于不同的社区，采用各种统计图可视化节点间平均距离、度分布、直径等等
  - [ ] 对于输入的一篇论文，推荐与之方向相近的几篇论文；对于输入的两（多）篇论文，计算其两两的相似度
  - [ ] 利用算法挖掘出不同社区之间的合作关系（如现在的AI4S），并与社会研究热点结合进行分析
  - [ ] 挖掘科研人员之间的人际关系社区，在地理上可视化不同研究机构之间的合作
  - [ ] 根据某一作者发表论文数量和被引次数的比例，结合其所处领域，判断其论文是否灌水
  - [ ] 尝试图中的最大群算法，判断作者间是否存在相互引用刷引用量的问题，也可以判断合作关系
  - [ ] 对于某一个作者，挖掘出其科研历史记录（发表数量，引用量，研究兴趣变化）
  - [ ] 学术小领域各个不同团体之间的变化关系，如何相互敌对合作，学派解体融合


### 数据集

- [Citation Network Dataset](https://www.aminer.cn/citation)
- [DBLP-Citation-network V9](https://lfs.aminer.cn/lab-datasets/citation/dblp.v9.zip): 3,680,007 papers and 1,876,067 citation relationships (2017-07-03)
- 格式
  - #*: paperTitle
  - #@: Authors
  - #t: Year
  - #c: publication venue
  - #index: index id of this paper
  - #%: the id of references of this paper (there are multiple lines, with each indicating a reference)
  - ~~#!: Abstract~~


### 参考资料

- [Papers with code](https://paperswithcode.com/dataset/dblp)
- [往届代码参考](https://github.com/Yikai-Wang/Social-Network-Mining-Based-on-Academic-Literatures)


### 运行方式
- 数据集处理
  - 下载数据集并解压
    ```bash
    mkdir -p data
    cd data
    wget -O dblp.v9.zip "https://lfs.aminer.cn/lab-datasets/citation/dblp.v9.zip"
    unzip dblp.v9.zip -d dblp.v9
    rm *.zip
    cd ..
    ```
  - 安装依赖库
    ```bash
    pip install -r requirements.txt
    ```
  - 在测试模式下运行代码
    ```bash
    python main.py --test
    ```
  - 处理全部数据集
    ```bash
    python main.py
    ```
- 可视化
  - 在 vscode 安装 live server 扩展
    ```pwsh
    code --install-extension ritwickdey.LiveServer
    ``` 
  - 按住 `Ctrl + Shift + P`，输入 live server，点击 Open with Live Server
  - 使用浏览器打开 http://127.0.0.1:5500/visualization/ 进入主页