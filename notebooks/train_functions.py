import pandas as pd
from sklearn.model_selection import GridSearchCV

scoring = dict(
    neg_root_mean_squared_error='neg_root_mean_squared_error',
    r_squared='r2')

def run_cv(X, y, estimator, params, scoring, groups=None, cv=None):
    # run grid search for hyperparameters
    grid_search = GridSearchCV(
                estimator=estimator, 
                param_grid=params,
                scoring=scoring,
                refit=False,
                cv=cv)

    cv = grid_search.fit(X, y, groups=groups)
    cv = pd.DataFrame({
        'model': [str(estimator)]*len(cv.cv_results_['params']),
        'params': cv.cv_results_['params'],
        'neg_root_mean_squared_error': cv.cv_results_['mean_test_neg_root_mean_squared_error'],
        'mean_test_r_squared': cv.cv_results_['mean_test_r_squared']}).sort_values('neg_root_mean_squared_error')
    
    cv_min = cv.loc[cv.neg_root_mean_squared_error.idxmax()]

    return cv, cv_min