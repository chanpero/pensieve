# 1. Prerequisites(setup.py):
## install:
  + mahimahi
  + apache2
  + selenium
  + pyvirtualdisplay
  + tensorflow
  + tflearn
  + xvfn, xserver-xephyr, tightvncserver
## cp
  + html, js, m4s, mpd　->　/var/www/html
## mkdir
</br>
</br>

# 2. Training
## 2.1 get_video_sizes_py
    store size of each chunk in file video_size_#(0 -> 5)
</br>

## 2.2 cp traces
</br>

## **2.3 multi_agent.py**
## main():
* 进程间通信队列：
  * net_params_queues = [16 * mp.Queue(1)]
  * exp_queues = [16 * mp.Queue(1)]
* 多进程的协调器：coordinator = mp.Process(target=**central_agent**, args=(net_params_queues, exp_queues))
* coordinator.start() -> **central_agent()** -> **testing()**
* load_trace(Train_traces)
  * load taces from './cooked_traces/' (127 files in all)
  * all_cooked_time = [127][n] (n represents each file contains how much data)
  * all_cooked_bw = [127][n]
  * all_file_names = [127 * trace_file_name]
* agents = [16 * mp.Process(target=**agent**, args=(i, all_cooked_time, all_cooked_bw, net_params_queues[i], exp_queues[i])))]
* foreach agents[i].start() [agent()]
  * ph
* coordinator.join()

**********************************************************************
## central_agent(net_param_queues, exp_queues):
* logging 配置日志 './results/log_central'，记录每一个Epoch的TD_loss、Avg_reward、Avg_entropy
* 创建A3C网络
* summary.FileWriter: 记录Graph
* train.Saver: 管理checkpoints
* 恢复model
* **while True: Run A3C**
  * 获取actor、critic的网络参数存入每个agent的net_param_queues
  * 初始化batch_len, total_reward, td_loss, entropy, total_agents, gradient_batch
  * 从exp_queues读取每个agent的s_batch,a_batch,r_batch,terminal,info， 计算gradients、td_batch，合计总的reward，td_loss，batch_len,agents,entropy
  * apply_gradients()
  * 记录训练信息至log_central，记录summary，并FileWriter写入
  * 每一百个epoch保存一下模型，并 -> **testing(epoch, model, test_logfile)
</br>
</br>
**********************************************************************

## testing(epoch, nn_model, log_file='log_test'):
* 重置结果文件./test_results
* -> python **rl_test.py** nn_model  生成测试结果保存在./test-results中
* 每个测试文件末尾列是reward，对每个文件reward求和，存入rewards
* 计算rewards中的min, 5percentile, mean, median, 95percentile, max, 并将epoch和这几个数据写入log_test
</br>
</br>
**********************************************************

## agent(agent_id, time, bw, net_params_queue, exp_queue):
* 初始化随机net_env
* tf.Session():
  * 创建A3C网络，获取设置net参数
  * 初始化bit_rate, action_vec, s|a|r_batch, entropy_record, time_stamp
  * while True:
    + **net_env.get_video_chunk(bitrate)** 获取模拟下载某一个chunk的数据
    + 更新time_stamp, 计算reward[linear/log/HD]，加入r_batch
    + 更新state
    + 将state传入actor.predict预测action_prob (softmax结果)
    + action_cumsum：action概率的累积分布
    + bit_rate 返回能够满足一个随机概率的最小bitrate
    + 计算entropy并记录
    + 记录日志： time_stamp(s), video_bitrate， buf_size(s), rebuf(s), chunk_size(byte), delay(ms), reward
    + 每100个chunk或者一个视频模拟结束，将s|a|r_batch, end_of_video, entropy_record传入exp_queue
    + 更新net_params
    + 清空s|a|r_batch, entropy_record
    + 如果一个视频结束，重置bitrate, action_vec, s|a_batch, 否则添加state, action 






**********************************************************
## rl_test.py:
+ load_traces
+ net_env = Fixed_Environment(time, bw) 固定质量1
+ 初始化log_file
+ tf.Session():
  + 创建A3C网络，恢复NN_Model,初始化一系列参数
  + while True:
    + **net_env.get_video_chunk(bitrate)** 获取模拟下载某一个chunk的数据
    + 更新time_stamp, 计算reward，加入r_batch
    + 记录日志： time_stamp(s), video_bitrate， buf_size(s), rebuf(s), chunk_size(byte), delay(ms), reward
    + 存入state中，state是过去8 chunk的模拟数据
    + 将state传入actor.predict预测action_prob (softmax结果)
    + action_cumsum：action概率的累积分布
    + bit_rate 返回能够满足一个随机概率的最小bitrate
    + s_batch添加state记录，计算entropy并记录
    + 一个trace_file或一个视频模拟结束后，清空s,a,r_batch，切换下一trace_file


************************************************

## fixed_env.py | env.py(随机):
+ __init__: 初始化模拟网络环境
+ get_video_chunk: 根据timestamp和bw推算，默认初始质量为1: 
  + delay: 下载下一个chunk所需时间
  + sleep_time: buffer超过threshold时需要暂停的时间
  + buffer_size: seconds
  + rebuf: 暂停缓冲时间
  + video_chunk_size
  + next_video_chunk_sizes: [6]对应各个质量的下一chunk大小
  + end_of_video: bool 是否结束
  + video_chunk_remain: 剩余chunk块数

***********************************************

## A3C.py
+ Actor: [输入状态，输出所有动作的分布]
  + __init__:
    + create_actor_network 创建网络 conv_1d、fully_conncted、relu、softmax...
    + 设置optimizer、loss_obj、gradient
+ Critic: [输入状态和动作，输出Value，动作由Actor推算]
  + __init__:
    + + create_critic_network 创建网络 conv_1d、fully_conncted、relu、linear...
    + + 设置optimizer、td_loss、gradient
+ compute_gradients: 计算actor_gradient,critic_gradient,td_batch
+ compute_entropy(action_prob): 计算actor.predict结果的entropy
+ build_summary: [创建scalar，用于tensorboard可视化]