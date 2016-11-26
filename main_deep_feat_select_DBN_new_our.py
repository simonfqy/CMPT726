#!/usr/bin/env python
"""
An example of how to use the DBN-based deep feature selection.
Yifeng Li
CMMT, UBC, Vancouver
Sep. 23, 2014
Contact: yifeng.li.cn@gmail.com
"""
#qsub -l procs=1,pmem=2000mb,walltime=36:00:00 -r n -N main_DFS_feature_selection -o main_DFS_feature_selection.out -e main_DFS_feature_selection.err -M yifeng.li.cn@gmail.com -m bea main_deep_feat_select_DBN.py
import os
#os.environ['THEANO_FLAGS']='device=cpu,base_compile=/var/tmp'
import sys
import time
import numpy
import deep_feat_select_DBN
import classification as cl
from gc import collect as gc_collect
import re

def obtain_error(classifier, test_set_x_org, test_set_y_org, batch_size=200, name="test"):
    test_set_y_pred,test_set_y_pred_prob,test_time=deep_feat_select_DBN.test_model(classifier, test_set_x_org, batch_size)

    print name + "_set_y_pred"
    print test_set_y_pred
    print "label"
    print test_set_y_org

    # calculating test error
    err = 0
    #for (test, lab) in (test_set_y_pred, test_set_y_org):
    #    summ += test != lab
    for (i, test) in enumerate(test_set_y_pred):
        err += test_set_y_org[i] != test
    print name + " error:"
    print err * 100.0 / len(test_set_y_org)

    #print "test_set_y_pred_prob[0:20]"
    #print test_set_y_pred_prob

    print name + "_time"
    print test_time
    return test_set_y_pred

numpy.warnings.filterwarnings('ignore') # Theano causes some warnings  

# taking the input parameters
#cell=sys.argv[1] # cell type
#wid=sys.argv[2] # window size

# load data
"""
A data set includes three files: 

[1]. A TAB seperated txt file, each row is a sample, each column is a feature. 
No row and columns allowd in the txt file.
If an original sample is a matrix (3-way array), a row of this file is actually a vectorized sample,
by concatnating the rows of the original sample.

[2]. A txt file including the class labels. 
Each row is a string (white space not allowed) as the class label of the corresponding row in [1].

[3]. A txt file including the name of features.
Each row is a string (white space not allowed) as the feature name of the corresponding column in [1].
"""
path="/home/yifengli/prog/my/deep_learning_v1_1/"
path = "./"

os.chdir(path)
data_dir="/home/yifengli/prog/my/deep_learning_v1_1/data/our/"
data_dir = "./ourdata/"


result_dir="/home/yifengli/prog/my/deep_learning_v1_1/result/"
result_dir = "./result/"


#cells=["GM12878","HepG2","K562","HelaS3","HUVEC","A549","MCF7","HMEC"]
#wids=[200,500,1000,2000,4000]
cells=["GM12878"]
wids=[200]

for cell in cells:
    for wid in wids:
        filename=data_dir+"Augdata.txt";
        data=numpy.loadtxt(filename,delimiter='\t',dtype='float32')
        filename=data_dir+"label.txt";
        classes=numpy.loadtxt(filename,delimiter='\t',dtype=object)
        filename=data_dir+"feature.txt"
        features=numpy.loadtxt(filename,delimiter='\t',dtype=object)
        

        #given=["A-E","I-E","A-P","I-P","A-X","I-X","UK"]
        #given=["A-E","I-E"]
        #given=["A-P","I-P"]
        #given=["A-E","A-P"]
        #given=["A-E","A-X"]
        #given=["A-P","A-X"]
        #given=["A-E","A-P","A-X"]
        #given=["A-E","I-E","A-P","I-P"]
        #given=["A-E","I-E","A-P","I-P","A-X","I-X"]
        #given=["I-E","I-P"]
        #data,classes,_=cl.take_some_classes(data,classes,given=given,others=None)
        
        #print "data"
        #print data

        #print "classes"
        #print classes

        #shuffling
        
        dataPlusClass = numpy.c_[ data , classes]

        numpy.random.shuffle(dataPlusClass)

        data = dataPlusClass[:,:-1]
        classes = dataPlusClass[:, -1]
    
        # balance the sample sizes of the classes
        rng=numpy.random.RandomState(100)
        data,classes,others=cl.balance_sample_size(data,classes,others=None,min_size_given=None,rng=rng)

        print "data.shape"
        print data.shape
        print "numpy.unique(classes)1"
        print numpy.unique(classes)

        #group=[["A-E"],["I-E"],["A-P"],["I-P"],["A-X"],["I-X"],["UK"]]
        #group=[["A-E","A-P"],["I-E","I-P","A-X","I-X","UK"]]
        #group=[["A-E","A-P","A-X"],["I-E","I-P","I-X","UK"]]
        #group=[["A-E"],["A-P"],["I-E","I-P","A-X","I-X","UK"]]
        #group=[["A-E"],["A-P"],["A-X"],["I-E","I-P","I-X","UK"]]
        #group=[["A-E"],["I-E"]]
        #group=[["A-P"],["I-P"]]
        #group=[["A-E"],["A-P"]]
        #group=[["A-E"],["A-X"]]
        #group=[["A-P"],["A-X"]]
        #group=[["A-E"],["A-P"],["A-X"]]
        #group=[["A-E","I-E"],["A-P","I-P"]]
        #group=[["A-E","A-P"],["I-E","I-P"]]
        #group=[["A-E","I-E"],["A-P","I-P"],["A-X","I-X"]]
        #group=[["A-E","A-P","A-X"],["I-E","I-P","I-X"]]
        #group=[["I-E"],["I-P"]]
        #classes=cl.merge_class_labels(classes,group)

        classes_unique,classes=cl.change_class_labels(classes)
        
        # set random state
        #numpy.random.seed(1000)
        rng=numpy.random.RandomState(100)
        data,classes,others=cl.balance_sample_size(data,classes,others=None,min_size_given=None,rng=rng)

        print "data.shape"
        print data.shape

        print "classes.shape"
        print classes.shape

        print "numpy.unique(classes)"
        print numpy.unique(classes)

        # partition the data
        train_set_x_org,train_set_y_org,valid_set_x_org,valid_set_y_org,test_set_x_org,test_set_y_org=cl.partition_train_valid_test(data,classes,ratio=(2,1,1),rng=rng)

        print "valid set shape"
        print valid_set_x_org.shape
        print valid_set_y_org.shape

        # normalization
        train_set_x_org,data_min,data_max=cl.normalize_col_scale01(train_set_x_org,tol=1e-10)
        valid_set_x_org,_,_=cl.normalize_col_scale01(valid_set_x_org,tol=1e-10,data_min=data_min,data_max=data_max)
        test_set_x_org,_,_=cl.normalize_col_scale01(test_set_x_org,tol=1e-10,data_min=data_min,data_max=data_max)

        # train
        # setting the parameter
        pretrain_lr=0.01
        finetune_lr=0.1
        alpha=0.1
        lambda2=1.0
        alpha1=0.001
        alpha2=0.01
        n_hidden=[120,64]
        pretraining_epochs=10
        training_epochs=1000
        batch_size=50


        # parameter
        #learning_rate=0.1
        #alpha=0.2
        #num_samplings_dfs=100
        
        #randomize_method="random_sampling_and_random_rescaling"
        #random_rescaling_alpha=0.5
        #random_sampling_portion=0.5
        #lambda1=0.001
        #lambda2=1.0
        #alpha1=0.001
        #alpha2=0.01
        #n_hidden=[120,64]
        #n_epochs=500
        #batch_size=50
        # normalization
        #train_set_x_org,data_min,data_max=cl.normalize_col_scale01(train_set_x_org,tol=1e-10)
        #test_set_x_org,_,_=cl.normalize_col_scale01(test_set_x_org,tol=1e-10,data_min=data_min,data_max=data_max)
        # randomized DFS

        #rdfs=randomized_dfs.randomized_dfs(n_in=len(features),n_out=num_classes)
        #feature_importance_rdfs,feature_weights_rdfs,training_time_rdfs=rdfs.train(train_set_x_org=train_set_x_org,
        #train_set_y_org=train_set_y_org,features=features,
        #num_samplings=num_samplings_dfs,
        #randomize_method=randomize_method,random_rescaling_alpha=random_rescaling_alpha,
        #random_sampling_portion=random_sampling_portion,
        #learning_rate=learning_rate, alpha=alpha,lambda1=lambda1, lambda2=lambda2,
        #alpha1=alpha1, alpha2=alpha2, n_hidden=n_hidden, n_epochs=n_epochs,
        #batch_size=batch_size,activation_func="relu", rng=rng,
        #dfs_select_method="top_num", dfs_threshold=0.001, dfs_top_num=10,
        #max_num_epoch_change_learning_rate=80,max_num_epoch_change_rate=0.8,learning_rate_decay_rate=0.8)




        activation_func='tanh'
        
        #if cell=="GM12878":
        #    lambda1s=numpy.arange(0.020,-0.0001,-0.0001)
        #if cell=="HepG2":
        #    lambda1s=numpy.arange(0.028,-0.0001,-0.0001)
        #if cell=="HelaS3":
        #    lambda1s=numpy.arange(0.028,-0.0001,-0.0001)
        #if cell=="K562":
        #    lambda1s=numpy.arange(0.025,-0.0001,-0.0001)
        lambda1s=[0.001]
        features_selected=[]
        weights_selected=[]
        weights=[]
        perfs=[]
        for i in range(len(lambda1s)):
            lambda1=lambda1s[i]
            classifier,training_time=deep_feat_select_DBN.train_model(train_set_x_org=train_set_x_org, train_set_y_org=train_set_y_org, 
                                                                      valid_set_x_org=valid_set_x_org, valid_set_y_org=valid_set_y_org, 
                                                                      pretrain_lr=pretrain_lr,finetune_lr=finetune_lr, alpha=alpha, 
                                                                      lambda1=lambda1, lambda2=lambda2, alpha1=alpha1, alpha2=alpha2,
                                                                      n_hidden=n_hidden, persistent_k=15,
                                                                      pretraining_epochs=pretraining_epochs, training_epochs=training_epochs,
                                                                      batch_size=batch_size, rng=rng)
 
            param0=classifier.params[0].get_value()
            param1=classifier.params[1].get_value()

            #print "param0"
            #print param0

            selected=abs(param0)>numpy.max(abs(param0))*0.5
            #selected=abs(param0)>0.001
            features_selected.append(features[selected])
            weights_selected.append(param0[selected])
            print 'Number of select variables:', sum(selected)
            print features[selected]
            #print  param0[selected]

            # compare features
            print "comapring features"
            with open("./ourdata/features.out", 'r') as f:
                bothsel = 0
                for feat in f:
                    tok = re.split("\t|\n", feat)
                    feat = tok[0]
                    if (feat in features[selected]):
                        bothsel += 1
            
            print "#features both selected: " + str(bothsel)
            with open("./ourdata/our_features.out", 'w') as f:
                for feat in features[selected]:
                    f.write(feat + '\n')

            print "param0"
            print param0
            weights.append(param0)

            # test error
            test_set_y_pred = obtain_error(classifier, test_set_x_org, test_set_y_org,name="test")

            # train error
            obtain_error(classifier, train_set_x_org, train_set_y_org, name="train")

            perf,conf_mat=cl.perform(test_set_y_org,test_set_y_pred,numpy.unique(train_set_y_org))
            perfs.append(perf)
            
            print "perf"
            print perf

            print "conf_mat"
            print conf_mat

        perfs=numpy.asarray(perfs)

        # save result        
        save_dir=result_dir + "_".join(classes_unique)
        try:
            os.makedirs(save_dir)
        except OSError:
            pass
        filename=save_dir + '/' + cell + "_" + str(wid) + "bp.txt"
        cl.write_feature_weight(weights,features,lambda1s,filename)
        filename=save_dir + '/' + cell + "_" + str(wid) + "bp_unique_yes.txt"
        cl.write_feature_weight2(weights,features,lambda1s,perfs[:,-3],uniqueness=True,tol=1e-3,filename=filename)
        filename=save_dir + '/' + cell + "_" + str(wid) + "bp_unique_no.txt"
        cl.write_feature_weight2(weights,features,lambda1s,perfs[:,-3],uniqueness=False,tol=1e-3,filename=filename)

        #save_dir=result_dir + "_".join(classes_unique)
        #filename=cell + "_" + str(wid) + "bp.txt"
        #cl.save_perform(save_dir,filename,perf=perf,std=None,conf_mat=conf_mat,classes_unique=classes_unique,training_time=training_time,test_time=test_time)
        gc_collect()
