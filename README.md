# apriori-analysis

## About Apriori
## 介绍
Apriori算法是常用的用于挖掘出数据关联规则的算法，它用来找出数据值中频繁出现的数据集合，找出这些集合的模式有助于我们做一些决策。比如在常见的超市购物数据集，或者电商的网购数据集中，如果我们找到了频繁出现的数据集，那么对于超市，我们可以优化产品的位置摆放，对于电商，我们可以优化商品所在的仓库位置，达到节约成本，增加经济效益的目的。下面我们就对Apriori算法做一个总结。

## 基本概念
关联分析
> 关联分析是一种在大规模数据集中寻找相互关系的任务。 这些关系可以有两种形式:
> 
> 频繁项集（frequent item sets）: 经常出现在一块的物品的集合。
> 
> 关联规则（associational rules）: 暗示两种物品之间可能存在很强的关系。

相关术语

关联分析（关联规则学习）: 下面是用一个 杂货店简单交易清单的例子来说明这两个概念，如下表所示:
|交易号码|	商品|
|-|-|
|0|	豆奶，莴苣|
|1|	莴苣，尿布，葡萄酒，甜菜|
|2|	豆奶，尿布，葡萄酒，橙汁|
|3|	莴苣，豆奶，尿布，葡萄酒|
|4|	莴苣，豆奶，尿布，橙汁|

* 频繁项集: {葡萄酒, 尿布, 豆奶} 就是一个频繁项集的例子。
* 关联规则: 尿布 -> 葡萄酒 就是一个关联规则。这意味着如果顾客买了尿布，那么他很可能会买葡萄酒。
* 支持度: 数据集中包含该项集的记录所占的比例。例如上图中，{豆奶} 的支持度为 4/5。{豆奶, 尿布} 的支持度为 3/5。
* 可信度: 针对一条诸如 {尿布} -> {葡萄酒} 这样具体的关联规则来定义的。这条规则的 可信度 被定义为 支持度({尿布, 葡萄酒})/支持度({尿布})，支持度({尿布, 葡萄酒}) = 3/5，支持度({尿布}) = 4/5，所以 {尿布} -> {葡萄酒} 的可信度 = 3/5 / 4/5 = 3/4 = 0.75。

    支持度 和 可信度 是用来量化 关联分析 是否成功的一个方法。 假设想找到支持度大于 0.8 的所有项集，应该如何去做呢？ 一个办法是生成一个物品所有可能组合的清单，然后对每一种组合统计它出现的频繁程度，但是当物品成千上万时，上述做法就非常非常慢了。 我们需要详细分析下这种情况并讨论下 Apriori 原理，该原理会减少关联规则学习时所需的计算量。

* k项集
如果事件A中包含k个元素，那么称这个事件A为k项集，并且事件A满足最小支持度阈值的事件称为频繁k项集。

* 由频繁项集产生强关联规则

    * K维数据项集LK是频繁项集的必要条件是它所有K-1维子项集也为频繁项集，记为LK-1　
    * 如果K维数据项集LK的任意一个K-1维子集Lk-1，不是频繁项集，则K维数据项集LK本身也不是最大数据项集。
    * Lk是K维频繁项集，如果所有K-1维频繁项集合Lk-1中包含LK的K-1维子项集的个数小于K，则Lk不可能是K维最大频繁数据项集。
    * 同时满足最小支持度阀值和最小置信度阀值的规则称为强规则。

对于Apriori算法，我们使用支持度来作为我们判断频繁项集的标准。Apriori算法的目标是找到最大的K项频繁集。这里有两层意思，首先，我们要找到符合支持度标准的频繁集。但是这样的频繁集可能有很多。第二层意思就是我们要找到最大个数的频繁集。比如我们找到符合支持度的频繁集AB和ABE，那么我们会抛弃AB，只保留ABE，因为AB是2项频繁集，而ABE是3项频繁集。那么具体的，Apriori算法是如何做到挖掘K项频繁集的呢？

Apriori算法采用了迭代的方法，先搜索出候选1项集及对应的支持度，剪枝去掉低于支持度的1项集，得到频繁1项集。然后对剩下的频繁1项集进行连接，得到候选的频繁2项集，筛选去掉低于支持度的候选频繁2项集，得到真正的频繁二项集，以此类推，迭代下去，直到无法找到频繁k+1项集为止，对应的频繁k项集的集合即为算法的输出结果。

可见这个算法还是很简洁的，第i次的迭代过程包括扫描计算候选频繁i项集的支持度，剪枝得到真正频繁i项集和连接生成候选频繁i+1项集三步。

## 算法实现
下面我们对Aprior算法流程做一个总结。

输入：数据集合D，支持度阈值α

输出：最大的频繁k项集

1. 扫描整个数据集，得到所有出现过的数据，作为候选频繁1项集。k=1，频繁0项集为空集。

2. 挖掘频繁k项集

    a)扫描数据计算候选频繁k项集的支持度
    
    b) 去除候选频繁k项集中支持度低于阈值的数据集,得到频繁k项集。如果得到的频繁k项集为空，则直接返回频繁k-1项集的集合作为算法结果，算法结束。如果得到的频繁k项集只有一项，则直接返回频繁k项集的集合作为算法结果，算法结束。

    c) 基于频繁k项集，连接生成候选频繁k+1项集。

3. 令k=k+1，转入步骤2。
从算法的步骤可以看出，Aprior算法每轮迭代都要扫描数据集，因此在数据集很大，数据种类很多的时候，算法效率很低。

## 结论
Aprior算法是一个非常经典的频繁项集的挖掘算法，很多算法都是基于Aprior算法而产生的，包括FP-Tree,GSP, CBA等。这些算法利用了Aprior算法的思想，但是对算法做了改进，数据挖掘效率更好一些，因此现在一般很少直接用Aprior算法来挖掘数据了，但是理解Aprior算法是理解其它Aprior类算法的前提，同时算法本身也不复杂，因此值得好好研究一番。

