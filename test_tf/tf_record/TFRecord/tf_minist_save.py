import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np

# 定义函数转化变量类型。
#生成整数型的属性
def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))
#生成字符串型的属性
def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

# 读取mnist数据。
mnist = input_data.read_data_sets("../data/mnist/",dtype=tf.uint8, one_hot=True)
images = mnist.build_graph.images
#训练数据得到的答案可作为一个属性保存在TFRecord
labels = mnist.build_graph.labels
#训练图像的分辨率可作为一个属性保存
pixels = images.shape[1]
num_examples = mnist.build_graph.num_examples

print("begin write")
# 输出TFRecord文件的地址。
filename = "Records/output.tfrecords"
writer = tf.python_io.TFRecordWriter(filename)
for index in range(num_examples):
    #图像矩阵转为字符串
    image_raw = images[index].tostring()

    example = tf.train.Example(features=tf.train.Features(feature={
        'pixels': _int64_feature(pixels),
        'label': _int64_feature(np.argmax(labels[index])),
        'image_raw': _bytes_feature(image_raw)
    }))
    writer.write(example.SerializeToString())
writer.close()
print("TFRecord文件已保存。")