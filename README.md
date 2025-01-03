<h2 align="center">基于 DBLP-v9 数据集的学术网络分析</h2>

<img width="1280" alt="visualization" src="https://github.com/user-attachments/assets/3b7e2ed0-889a-4f0e-99e6-c70284943b03" />

- [选题及任务](#选题及任务)
- [数据集](#数据集)
- [项目结构](#项目结构)
- [数据集处理](#数据集处理)
- [可视化系统](#可视化系统)
- [链接预测](#链接预测)

### 选题及任务
- 选题：社交网络节点分析与社区挖掘
- 任务：
  - [x] 应用某种社区挖掘算法划分网络中的不同社区，并用可视化技术展现出（具体展示工具不做硬性要求）。
  - [x] 对网络做进一步分析，例如应用各种节点的中心性度量算法将最具影响力/权威性/中枢性的节点识别并凸显出来，通过图、表等形式展现网络的各种属性度量结果（如节点间平均距离、度分布、图/社区的直径、网络结构演化等）。
  - 附加任务（非必做，可任选其一）：
    - [x] 链接预测：利用网络数据集提供的信息，设计一种机器学习模型预测网络中边的形成，同时说明预测模型性能评价的方法和结果。针对不同网络数据集，链接预测可对应不同的应用任务，如好友预测、科研合作预测、购买行为预测等。
    - 节点分类：设计一种模型判别网络中各节点的类别，同时说明模型性能评价的方法和结果。根据实际数据集可以实现二分类或多分类。

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

### 项目结构

```txt
├─.github/workflows   # Github CI 工作流，在测试模式下运行代码，检查代码是否 format
├─.ipynb              # 对预处理后 author 与 paper 数据进行探索性分析的 notebook
|  ├─author.ipynb
│  └─paper.ipynb
├─CentralityMeasure   # 中心性度量代码
│  ├─centrality.py        # 计算度中心度和 PageRank 中心度
│  └─diameter.py          # 计算社区的直径
├─CommunityMining     # 社区挖掘代码
│  ├─author_community.py  # 划分 author 社区，过滤掉异常数据
│  ├─paper_community.py   # 划分 paper 社区，可选取多种算法(Label Propagration, Multi-Level)
│  └─louvain.py           # Louvain(Leiden) 算法划分 paper 社区
├─data/*              # 数据集位置
├─LinkPrediction      # 链接预测代码
│  ├─emb/
│  ├─data.zip             # 数据集
│  ├─model.py             # 定义 LACE, GLACE 模型
│  ├─pipeline.py          # 辅助函数、训练函数
│  └─train.py             # 定义 parser，主函数
├─logs/*              # 项目运行时自动生成的日志
├─PostProcess         # 生成可视化数据代码
│  ├─filter_author.py     # filter 用于展示的 author id
│  ├─filter_paper.py      # filter 用于展示的 paper id
│  ├─combine_author.py    # 根据 author id 生成需要的可视化数据
│  └─combine_paper.py     # 根据 paper id 生成需要的可视化数据
├─report/*            # 项目报告，包含 tex 文件，图片文件和 pdf
├─static              # 可视化代码位置
│  ├─css/    
│  ├─js/                  # 可视化代码
│  ├─lib/                 # d3-v7 库代码
│  ├─index.html           # 可视化主界面
│  ├─author.html          # author 分界面
│  └─paper.html           # paper 分界面
├─test/*              # 用于测试代码可运行性
├─utils               # 辅助函数 + 预处理函数
│  ├─loader.py            # 定义加载函数，加载预处理生成的 author/paper 数据
│  ├─logger.py            # 日志器
│  ├─preprocess.py        # 预处理函数
│  ├─seeder.py            # 随机数种子
│  └─wrapper.py           # 装饰器，定义 `@timer` 记录函数运行时间
├─visualize/*         # 可视化数据集位置，运行 `main.py` 自动生成
├─config.yaml         # 项目配置文件，记录数据位置
├─main.py             # 主函数，包装预处理、社区挖掘、中心性度量、生成可视化数据所有逻辑
├─README.md           
└─requirements.txt
```

### 数据集处理
- 下载数据集并解压
  ```bash
  mkdir -p data
  cd data
  wget -O dblp.v9.zip "https://lfs.aminer.cn/lab-datasets/citation/dblp.v9.zip"
  unzip dblp.v9.zip -d dblp.v9
  rm dblp.v9.zip
  cd ..
  ```
- 安装依赖库
  ```bash
  pip install -r requirements.txt
  ```
- 在测试数据集上验证项目是否可运行
  ```bash
  # 仅测试预处理部分代码
  python main.py --test
  # 会覆盖所有可视化数据，仅在开发过程中使用！！！
  # 若不希望覆盖完整可视化数据，请跳过该命令
  python main.py --test --all
  ```
- 处理全部数据集(数据集预处理、社区挖掘、中心性度量、生成用于可视化的数据) 
  > - 可在 `main.py` L36 选择是否打开 `PREPROCESS`。若已生成预处理数据，则可将其设为 `False` 
  > - 初始项目文件中的 `visualize/` 文件夹下即为完整的可视化数据，若上一步在测试数据集上测试全部代码，则会覆盖这些数据，需要重新在完整数据集上运行重新生成可视化数据
  > - 运行完全部代码预计8分钟
  ```bash
  python main.py
  ```

### 可视化系统
- 在 vscode 安装 live server 扩展
  ```pwsh
  code --install-extension ritwickdey.LiveServer
  ``` 
- 按住 `Ctrl + Shift + P`，输入 live server，点击 Open with Live Server
- 使用浏览器打开 http://127.0.0.1:5500/static/ 进入主页
- `author.html`
- `paper.html`
  - 左上角社区划分图
    - 拖拽节点
    - 界面放大缩小
    - 上方中间时间轴可拖动，展示社区演化历史
    - 单击节点，联动更新右上角信息表和下方度分布图，展示数据为该节点对应社区
    - 双击节点，联动更新，展示数据为全部数据
  - 右上角信息表
    - 具有分页功能，可点击跳转查看
    - 按 citation 从大到小排列
  - 左下角 bar plot
  - 下部分中间 degree distribution
  - 右下角 donut chart
  - 所有界面均支持平滑更新、标签展示具体信息、鼠标悬浮交互效果

### 链接预测
- 解压缩数据集
  ```bash
  cd LinkPrediction
  unzip data.zip -d data
  rm data.zip # optional
  cd ..
  ```
- 训练GLACE model
  ```bash
  python ./LinkPrediction/train.py cora_ml glace \
  --proximity first-order --embedding_dim 128 \
  --batch_size 32 --K 5 \
  --learning_rate 0.001 --num_batches 100000
  ```
