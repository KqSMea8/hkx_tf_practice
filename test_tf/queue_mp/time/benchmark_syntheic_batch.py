# [1484611992] time[  0.00] step[       420] speed[613695]
# [1484611992] time[  0.00] step[       440] speed[501141]
# [1484611992] time[  0.01] step[       460] speed[351428]
# [1484611992] time[  0.00] step[       480] speed[450032]
# [1484611993] time[  0.14] step[       500] speed[ 14419]
# [1484611993] time[  0.15] step[       520] speed[ 13662]
# [1484611993] time[  0.14] step[       540] speed[ 13960]
# [1484611993] time[  0.15] step[       560] speed[ 13069]

import tensorflow as tf
import time


steps_to_validate = 200
epoch_number = 2
thread_number = 2
batch_size = 100

capacity = 2*10**6
# don't use too high of limit, 10**9 hangs (overflows to negative in TF?)
a_queue = tf.train.range_input_producer(limit=10**3, capacity=capacity)

# use size of 2 or get TypeError: 'Tensor' object is not iterable.
# (possibly singleton list get auto-packed into a single Tensor)
[b, _] = tf.train.batch([a_queue.dequeue()]*2, batch_size=100,
                        capacity=capacity)


config = tf.ConfigProto(log_device_placement=True)
config.operation_timeout_in_ms=5000   # terminate on long hangs
sess = tf.InteractiveSession("", config=config)

tf.train.start_queue_runners()

with open("syntheic_graph.json", "w") as graph:
    graph.write(str(tf.get_default_graph().as_graph_def()))  # 打印图结构

def let_queue_repopulate(size_tensor, min_elements=100000, sleep_delay=0.5):
    """Wait until queue has enough elements."""
    #size2 = "input_producer/fraction_of_2000000_full/fraction_of_2000000_full_Size:0"
    size2 = "input_producer/input_producer_Size:0"
    while sess.run(size_tensor) < min_elements:
        print("Size1: %d, size2: %d" %tuple(sess.run([size_tensor, size2])))
        time.sleep(sleep_delay)

step = 0
start_time = time.time()
while True:
    step+=1
    let_queue_repopulate(size_tensor="batch/fifo_queue_Size:0") # 当batch队列里的元素过少，就等待
    sess.run(b.op) # 获取batch元素
    if step % steps_to_validate == 0:
        end_time = time.time()
        sec = (end_time - start_time)
        print("[{}] time[{:6.2f}] step[{:10d}] speed[{:6d}]".format(
            str(end_time).split(".")[0],sec, step,
            int((steps_to_validate*batch_size)/sec)
        ))
        start_time = end_time