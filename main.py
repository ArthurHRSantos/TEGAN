import numpy as np
import os
import h5py
import tensorflow as tf

from lib.defaultFlags import defaultFlags
from lib.model import TEResNet
from lib.ops import print_configuration_op
from lib.readTFRecord import getTFRecordFilenamesIn 

FLAGS = defaultFlags()

# Print the configuration of the model
print_configuration_op(FLAGS)

# Check the output_dir is given
if FLAGS.output_dir is None:
    raise ValueError('The output directory is needed')

# Check the output directory to save the checkpoint
if not os.path.exists(FLAGS.output_dir):
    os.mkdir(FLAGS.output_dir)

# Check the summary directory to save the event
# if not os.path.exists(FLAGS.summary_dir):
#     os.mkdir(FLAGS.summary_dir)

filenames_HR = getTFRecordFilenamesIn(FLAGS.input_dir_HR)
print("Using files: ", filenames_HR)
if len(filenames_HR) % FLAGS.batch_size != 0:
    print("You have been warned!!! Tread with CAUTION!!!")

net = TEResNet(filenames_HR, FLAGS)

with tf.Session() as sess:
    net.initialize(sess)
    print("Finished initializing :D")

    if FLAGS.mode == 'train':

        for i in range(FLAGS.max_iter):
            try:
                loss, step, train = net.optimize(sess)

                with open('log.dat', 'a') as f:
                    f.write('%06d %26.16e\n' %(step, loss))
            except tf.errors.OutOfRangeError:
                # training terminated
                break

            print("Iteration {}: update loss = {}".format(i, loss))

    elif FLAGS.mode == 'test':
        HR, LR, HR_out, loss = net.evaluate(sess)

        print("Saving test data to {}".format(os.path.join(FLAGS.output_dir, 'test_data.h5')))
        h5f = h5py.File(os.path.join(FLAGS.output_dir, 'test_data.h5'), 'w')
        h5f.create_dataset('HR', data=HR)
        h5f.create_dataset('LR', data=LR)
        h5f.create_dataset('output', data=HR_out)
        h5f.close()

        print("Test loss: ", loss)
