import pandas as pd
import numpy as np
from sklearn import preprocessing

from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow import keras
from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense

from IPython.display import clear_output


def build_spectrum (data,do_spectrum = False ,spect = 0.5, random_state = 1):
    
    """ Function that build a specific spectrum of the class y = 1 from the bank-additional-full.csv.
    It sets a label encoder for columns that aren't numeric and remove the column that are highly correlated, such as duration.
    It returns one dataframe.
    
        Inputs: - data : Dataframe of raw data
                - spect : Pourcentage of the class y = 0. Default value is 0.5. Must between 0.5 and 1.
                - random_state : Originally set at 1, it is used for sampling. For reproductibility, keep it at the same value.
                - do_spectrum : If not set, the dataset return is the preprocessed data with its original balance. Must be set to True, if we want to build a spectrum.
                
        Output: Dataframe with the desired spectrum."""
    
    assert((spect>=0.5)&(spect<=1)), 'Pourcentage of the spectrum is not in the good range'
    
    onehot_data = data.apply(preprocessing.LabelEncoder().fit_transform)
    onehot_data = onehot_data.drop(columns=['duration'])

    yes_onehot_data = onehot_data.loc[onehot_data['y']== 1]
    no_onehot_data = onehot_data.loc[onehot_data['y']== 0]

    final_size_set = 2*yes_onehot_data.size

    size_set = yes_onehot_data.size + no_onehot_data.size
    spect_no = no_onehot_data.size/size_set
    spect_yes = yes_onehot_data.size/size_set

    if do_spectrum:

        size_no = round((spect)*final_size_set)
        size_yes = final_size_set-size_no
        frac = size_no/no_onehot_data.size
        no_onehot_data = no_onehot_data.sample(frac = frac, random_state=random_state)
        frac = size_yes/yes_onehot_data.size
        yes_onehot_data = yes_onehot_data.sample(frac = frac, random_state=random_state)


        spect_no = no_onehot_data.size/final_size_set
        spect_yes = yes_onehot_data.size/final_size_set

    print("Fraction of No :", spect_no, "Fraction of Yes :", spect_yes, sep='\n')
    clear_output(wait=True)
        
    return pd.concat([no_onehot_data, yes_onehot_data], ignore_index=True)



def build_plot_benchmark(spects, sgd_metric, adam_metric, radam_metric, metric_name, activation):
    plt.style.use('seaborn-whitegrid')
    plt.plot(spects, sgd_metric, label='SGD')
    plt.plot(spects, adam_metric, label='Adam')
    plt.plot(spects, radam_metric, label='RAdam')
    plt.xlabel('Balance of the data set[-]')
    plt.ylabel('{}[-]'.format(metric_name))
    plt.title('{} against spectrum balance with {}'.format(metric_name, activation))
    plt.legend(loc='upper right')
    plt.savefig('figures/{}-spect-{}.png'.format(metric_name, activation))


def build_validation_loss_plot(adam, radam, sgd,spect):
    plt.style.use('seaborn-whitegrid')
    plt.plot(adam, label='Adam')
    plt.plot(radam, label='RAdam')
    plt.plot(sgd, label='SGD')
    plt.xlabel('Epochs[-]')
    plt.ylabel('Loss[-]')
    plt.title('Validation loss against epochs for {}% spectrum'.format(spect))
    plt.legend(loc='lower right', frameon = True)
    plt.savefig('figures/loss-epochs-{}.png'.format(spect))

def build_keras (x,y):
    """Adapt the size of inputs """
    x_keras = np.array(x)
    y_keras = np.array(y)
    y_keras = y_keras.reshape(y_keras.shape[0], 1)
    return x_keras, y_keras

def build_model(activation):
    """Build the neural network"""
    model = Sequential()
    model.add(Dense(10, input_dim=19, activation=activation))
    model.add(Dense(1, activation='sigmoid'))
    return model

def recall_m(y_true, y_pred):
    """Compute the recall with the true value"""
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def precision_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

    
    
    
