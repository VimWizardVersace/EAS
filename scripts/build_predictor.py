from sklearn.externals import joblib
from sklearn import preprocessing
from sklearn import grid_search
from sklearn import svm
import csv
import os


def parse_data(file_name, save_scaler=True):
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

    scaler = preprocessing.StandardScaler().fit(X)
    X_scaled = scaler.transform(X)

    if save_scaler:
        joblib.dump(scaler, 'scaler/scaler.pkl')    

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


def train_predictor(data):
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

    return predictor


def test_predictor(data, predictor):
    """ Goes through all the testing data, and returns the mean
    absolute percent error based off the predicted and actual transcode
    times
    """
    errors = []

    for i, vec in enumerate(data['X']['testing']):
        actual = data['T']['testing'][i]
        predicted = predictor.predict(vec)[0]
        errors.append(abs((actual - predicted)/actual) * 100.0)

    return round(sum(errors) / len(errors))


def save_predictor(predictor, save_directory='predictor'):
    """ Saves a predictor using the in-house scikit pickle module. Also
    saves method of data normalization, so it can be recreated later
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    joblib.dump(predictor, save_directory + '/predictor.pkl')


def load_predictor(load_directory='predictor'):
    """
    """
    if not os.path.exists(load_directory):
        raise IOError('No predictor module found')

    return joblib.load(load_directory + '/predictor.pkl')


if __name__ == '__main__':
    unsplit_data, scaler = parse_data('conversions_total.csv')
    data = split_data(unsplit_data, 2/3.)
    predictor = train_predictor(data)
    error = test_predictor(data, predictor)
    print 'Mean absolute percent error: ' + str(error) + '%'
