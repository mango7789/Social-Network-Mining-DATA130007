<h2 align="center">社交网络挖掘期末项目</h2>


### 选题

<details>
<summary> 社交网络节点分析与社区挖掘 </summary>

- a. 应用某种社区挖掘算法划分网络中的不同社区，并用可视化技术展现出（具体展示工具不做硬性要求）。
- b. 对网络做进一步分析，例如应用各种节点的中心性度量算法将最具影响力/权威性/中枢性的节点识别并凸显出来，通过图、表等形式展现网络的各种属性度量结果（如节点间平均距离、度分布、图/社区的直径、网络结构演化等）。
- c. 附加任务（非必做，可任选其一）：
  - 链接预测：利用网络数据集提供的信息，设计一种机器学习模型预测网络中边的形成，同时说明预测模型性能评价的方法和结果。针对不同网络数据集，链接预测可对应不同的应用任务，如好友预测、科研合作预测、购买行为预测等。
  - 节点分类：设计一种模型判别网络中各节点的类别，同时说明模型性能评价的方法和结果。根据实际数据集可以实现二分类或多分类。

</details>

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


### 数据集处理 (Python 3.11)
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
- 在测试模式下运行代码
  ```bash
  python main.py --test
  ```
- 处理全部数据集
  ```bash
  python main.py
    ```

### 可视化 (d3.js v7)
  - 在 vscode 安装 live server 扩展
    ```pwsh
    code --install-extension ritwickdey.LiveServer
    ``` 
  - 按住 `Ctrl + Shift + P`，输入 live server，点击 Open with Live Server
  - 使用浏览器打开 http://127.0.0.1:5500/static/ 进入主页

### 链接预测
  - 训练GLACE model
    ```bash
    cd LinkPrediction
    unzip data.zip -d data
    rm data.zip
    cd ..
    python ./LinkPrediction/train.py cora_ml glace \
    --proximity first-order --embedding_dim 128 \
    --batch_size 32 --K 5 \
    --learning_rate 0.001 --num_batches 100000
    ```
