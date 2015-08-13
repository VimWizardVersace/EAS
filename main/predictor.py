from sklearn.externals import joblib
from sklearn import preprocessing
from sklearn import grid_search
from sklearn import svm
from math import ceil
import time
import json
import csv
import os

from ingest import read_index


def parse_data(file_name):
    """ Parse csv conversion data, assuming it is in the same format
    given by  gather.py, and assuming that the codecs in question are
    not relevant (in other words, that the conversions are always done
    from codec A to codec B). Returns a tuple containing the X and T
    data
    """
    data_file = open(file_name, 'r')
    reader = csv.reader(data_file, delimiter=',')

    X = []
    T = []
    for row in reader:
        in_resolution = row[4].split('x')
        out_resolution = row[12].split('x')

        data_vec = [float(row[1]), float(row[2]), float(row[6]), float(row[7]),
                    float(row[8]), float(row[10]), float(in_resolution[0]),
                    float(in_resolution[1]), float(out_resolution[0]),
                    float(out_resolution[1])]
        X.append(data_vec)
        T.append(float(row[14]))

    return X, T


def scale_data((X, T), save=True):
    """ Scale data, save scaler object if requested, and return the
    scaler so future data can be scaled in the same manner
    """
    scaler = preprocessing.StandardScaler().fit(X)
    X_scaled = scaler.transform(X)

    if save:
        save_scaler(scaler)

    return (X_scaled, T), scaler


def split_data((X, T), split_fraction):
    """ Splits the data according to the given fraction, where some
    part is considered training data and the rest is considered testing
    data. The data is returned as a dictionary to distinguish between
    the X/T training/testing data.
    """
    split_length = int(split_fraction * len(X))

    X_train = X[:split_length]
    T_train = T[:split_length]
    X_test = X[split_length:]
    T_test = T[split_length:]
    data = {
        'X': {
            'training': X_train,
            'testing': X_test
        },
        'T': {
            'training': T_train,
            'testing': T_test
        }
    }

    return data


def train_predictor(data, save=True):
    """ Does a grid search over the data to find the best parameters
    for the support vector regression, then fits the machine to the
    training data, and returns the predictor object
    """
    param_grid = [
        {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
        {'C': [1, 10, 100, 1000], 'gamma': [0.0, 1e-3, 1e-4],
         'kernel': ['rbf']},
    ]

    svr = svm.SVR()
    predictor = grid_search.GridSearchCV(svr, param_grid)
    predictor.fit(data['X']['training'], data['T']['training'])

    if save:
        save_predictor(predictor)

    return predictor


def test_predictor(data, predictor=None):
    """ Goes through all the testing data, and returns the mean
    absolute percent error based off the predicted and actual transcode
    times
    """
    if not predictor:
        predictor = load_predictor()

    errors = []

    for i, vec in enumerate(data['X']['testing']):
        actual = data['T']['testing'][i]
        predicted = predictor.predict(vec)[0]
        errors.append(abs((actual - predicted)/actual) * 100.0)

    return round(sum(errors) / len(errors))


def save_predictor(predictor):
    """ Saves a predictor using the in-house scikit pickle module. Also
    saves method of data normalization, so it can be recreated later
    """
    save_directory = 'predictor'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    joblib.dump(predictor, save_directory + '/predictor.pkl')


def load_predictor():
    """ Load and return predictor module """
    load_directory = 'predictor'

    if not os.path.exists(load_directory):
        raise IOError('No predictor module found')

    return joblib.load(load_directory + '/predictor.pkl')


def save_scaler(scaler):
    """ Saves a predictor using the in-house scikit pickle module. Also
    saves method of data normalization, so it can be recreated later
    """
    save_directory = 'scaler'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    joblib.dump(scaler, save_directory + '/scaler.pkl')


def load_scaler():
    """ Load and return scaler module """
    load_directory = 'scaler'

    if not os.path.exists(load_directory):
        raise IOError('No scaler module found')

    return joblib.load(load_directory + '/scaler.pkl')


def load_config():
    """ Load and return default configuration (found on config.conf) """

    if not os.path.exists('config.json'):
        raise IOError('No default configuration found')

    return json.load(open('config.json'))


def generate_vec(filename, transcode_config):
    """ Generates the vector, using the input and output data on the video,
    used by the machine learning algorithm to predict transcode time. The data
    must be in the same order as when the machine learning algorithm was
    trained, which is defined as follows:

    [Video Duration, Input FPS, I frames, B frames, P frames, Output FPS,
    Input width, Input height, Output width, Output height]
    """
    index = read_index()
    input_info = index[filename]

    o_size = transcode_config['video']['size']
    o_width = int(o_size.split('x')[0])
    o_height = int(o_size.split('x')[0])

    vec = [input_info['duration'],
           input_info['fps'],
           input_info['i frames'],
           input_info['b frames'],
           input_info['p frames'],
           float(transcode_config['video']['fps']),
           input_info['width'],
           input_info['height'],
           o_width,
           o_height]

    return vec


def predict(filename, predictor=None, scaler=None, config=None):
    """ Makes a prediction of based off unscaled data passed to the
    function, loading the predictor and scaler from files if none are
    passed to the function
    """
    if not scaler:
        scaler = load_scaler()
    if not predictor:
        predictor = load_predictor()
    if not config:
        config = load_config()

    vec = generate_vec(filename, config)
    scaled_vec = scaler.transform([vec])[0]
    time_float = predictor.predict(scaled_vec)[0]
    time_est = str(int(ceil(time_float/10.)) * 10) + 's'
    time_str = time.strftime('%-M minutes %-S seconds', time.gmtime(time_est))
    print 'Predicted transcode time for', filename, 'is about', time_str
    return time_float


# Running this file will train a predictor based off the training data found in
# the specified csv file
if __name__ == '__main__':
    training_data = 'conversions_total.csv'

    raw_data = parse_data(training_data)
    scaled_data, scaler = scale_data(raw_data)
    final_data = split_data(scaled_data, 1/30.)
    predictor = train_predictor(final_data)