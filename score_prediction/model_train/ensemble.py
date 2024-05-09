import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from skopt.space import Real, Categorical, Integer
from model_train.get_data import get_data
from skopt import BayesSearchCV
from tqdm import tqdm
import lightgbm as lgb
import xgboost as xgb
import numpy as np
import joblib,json

n_folds = 5

def rmsle_cv(model, X_train, y_train):
    kf = KFold(n_folds, shuffle=True, random_state=42).get_n_splits(X_train.values)
    rmse= np.sqrt(-cross_val_score(model, X_train.values, y_train, scoring="neg_mean_squared_error", cv = kf))
    return(rmse)

def ensemble_model_train():
    final_df = get_data()
    X = final_df.drop('score', axis=1)
    y = final_df['score']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 모델 정의
    models = {
        'GradientBoosting' : GradientBoostingRegressor(n_estimators=3000, learning_rate=0.05,
                                            max_depth=4, max_features='sqrt',
                                            min_samples_leaf=15, min_samples_split=10, 
                                            loss='huber', warm_start=True),

        'XGBoost' : xgb.XGBRegressor(colsample_bytree=0.4603, gamma=0.0468, 
                                    learning_rate=0.05, max_depth=3, 
                                    min_child_weight=1.7817, n_estimators=2200,
                                    reg_alpha=0.4640, reg_lambda=0.8571,
                                    subsample=0.5213, verbosity=0,
                                    random_state=7, n_jobs=-1),

        'LightGBM' : lgb.LGBMRegressor(objective='regression', num_leaves=5,
                                    learning_rate=0.05, n_estimators=720,
                                    max_bin=55, bagging_fraction=0.8,
                                    bagging_freq=5, feature_fraction=0.2319,
                                    feature_fraction_seed=9, bagging_seed=9,
                                    min_data_in_leaf=6, min_sum_hessian_in_leaf=11),

        'RandomForest' : RandomForestRegressor(n_estimators=3000, 
                                        max_depth=4, max_features='sqrt',
                                        min_samples_leaf=15, min_samples_split=10),
    }

    model_scores = {}
    # 폴더 확인 및 생성
    base_model_path = 'score_prediction/model/base_model'
    if not os.path.exists(base_model_path):
        os.makedirs(base_model_path)

    for model_name, model in tqdm(models.items()):  # 모델 훈련 및 저장
        model.fit(X_train, y_train)

        rmsle_score = rmsle_cv(model, X_train, y_train).mean()
        model_scores[model_name] = rmsle_score

        model_file_path = f'{base_model_path}/{model_name}.joblib'
        joblib.dump(model, model_file_path)
        
        print(f'{model_name} model with RMSLE {rmsle_score} saved successfully at {model_file_path}.')

    # 모든 RMSLE 점수를 한 개의 JSON 파일에 저장
    score_file_path = f'{base_model_path}/model_scores.json'
    with open(score_file_path, 'w') as score_file:
        json.dump(model_scores, score_file)

    print(f'All model scores saved successfully in {score_file_path}.')

def fine_tuning(user_id):
    # 사용자 데이터 로드
    fine_tune_data = get_data(user_id)
    
    if len(fine_tune_data) > 5:
        X = fine_tune_data.drop('score', axis=1)
        y = fine_tune_data['score']

        # 사용자 폴더 생성
        user_folder = f'score_prediction/model/{user_id}'
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        model_names = ['GradientBoosting', 'XGBoost', 'LightGBM', 'RandomForest']
        model_classes = {
            'GradientBoosting': GradientBoostingRegressor(),
            'XGBoost': xgb.XGBRegressor(),
            'LightGBM': lgb.LGBMRegressor(),
            'RandomForest': RandomForestRegressor()
        }

        # 각 모델의 하이퍼파라미터 범위 설정
        param_spaces = {
            'GradientBoosting': {
                'n_estimators': Integer(100, 500),
                'max_depth': Integer(3, 10),
                'learning_rate': Real(0.01, 0.2, 'log-uniform'),
            },
            'XGBoost': {
                'n_estimators': Integer(100, 500),
                'max_depth': Integer(3, 10),
                'learning_rate': Real(0.01, 0.2, 'log-uniform'),
            },
            'LightGBM': {
                'n_estimators': Integer(100, 500),
                'num_leaves': Integer(30, 90),
                'learning_rate': Real(0.01, 0.2, 'log-uniform'),
            },
            'RandomForest': {
                'n_estimators': Integer(100, 500),
                'max_depth': Integer(3, 10),
            }
        }

        fine_tuned_scores = {}

        for model_name in model_names:
            model = model_classes[model_name]
            search_space = param_spaces[model_name]

            # 베이지안 최적화 실행
            opt = BayesSearchCV(
                estimator=model,
                search_spaces=search_space,
                scoring='neg_mean_squared_error',
                n_iter=30,
                cv=3,
                n_jobs=-1,
                return_train_score=False
            )

            opt.fit(X, y)

            # 최적의 모델 저장
            best_model = opt.best_estimator_
            fine_tuned_model_path = f'{user_folder}/{model_name}_fine_tuned.joblib'
            joblib.dump(best_model, fine_tuned_model_path)

            # 최적화 결과 저장
            #fine_tuned_scores[model_name] = -opt.best_score_
            rmsle_score = rmsle_cv(best_model, X, y).mean()
            fine_tuned_scores[model_name] = rmsle_score

            print(f'{model_name} model fine-tuned and saved in {fine_tuned_model_path}. Best Score: {-opt.best_score_}')

        # 업데이트된 점수를 JSON 파일에 저장
        fine_tuned_score_path = f'{user_folder}/{user_id}_fine_tuned_model_scores.json'
        with open(fine_tuned_score_path, 'w') as score_file:
            json.dump(fine_tuned_scores, score_file)

        print(f'Updated fine-tuned RMSLE scores saved in {fine_tuned_score_path}.')

#fine_tuning('kimdo0478@gmail.com')
ensemble_model_train()