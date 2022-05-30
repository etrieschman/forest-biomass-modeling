import pandas as pd
from sklearn.model_selection import GridSearchCV

scoring_default = dict(
    neg_root_mean_squared_error='neg_root_mean_squared_error',
    neg_mean_absolute_error='neg_mean_absolute_error',
    r_squared='r2')

def run_cv(X, y, estimator, params, scoring, groups=None, cv=None):
    # run grid search for hyperparameters
    grid_search = GridSearchCV(
                estimator=estimator, 
                param_grid=params,
                scoring=scoring,
                refit=False,
                cv=cv,
                verbose=1)

    cv = grid_search.fit(X, y, groups=groups)
    
    cv_df = pd.DataFrame({
        'model': [str(estimator)]*len(cv.cv_results_['params']),
        'params': cv.cv_results_['params'],
        'rmse': -1 * cv.cv_results_['mean_test_neg_root_mean_squared_error'],
        'mae': -1 * cv.cv_results_['mean_test_neg_mean_absolute_error']}
    ).sort_values('rmse')
    
    if 'r_squared' in scoring.keys():
        cv_df.loc[:, 'r_sq'] = cv.cv_results_['mean_test_r_squared']
        
    cv_df_min = cv_df.loc[cv_df.rmse.idxmin()]

    return {'all':cv_df, 'min':cv_df_min}