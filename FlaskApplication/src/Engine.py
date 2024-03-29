
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from ML_Pipeline.utlis import read_data
from sklearn.model_selection import train_test_split
from ML_Pipeline.models import model_zoo, evaluate_models
from ML_Pipeline.hyperparameter import model, parameters
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from lightgbm import LGBMClassifier
from ML_Pipeline.feature_eng import AddFeatures
from ML_Pipeline.scaler import CustomScaler
from ML_Pipeline.encoding import CategoricalEncoder
from sklearn.metrics import roc_auc_score, f1_score, recall_score, confusion_matrix, classification_report
import joblib


df = read_data("../input/Churn_Modelling.csv")


target_var = ['Exited']
cols_to_remove = ['RowNumber', 'CustomerId']


y = df[target_var].values
df.drop(cols_to_remove, axis=1, inplace=True)


df_train_val, df_test, y_train_val, y_test = train_test_split(df, y.ravel(),
                                                              test_size=0.1,
                                                              random_state=42)


df_train, df_val, y_train, y_val = train_test_split(df_train_val,
                                                    y_train_val,
                                                    test_size=0.12,
                                                    random_state=42)


X = df_train.drop(columns=['Exited'], axis=1)
y = y_train.ravel()
weights_dict = {0: 1.0, 1: 3.93}
_, num_samples = np.unique(y_train, return_counts=True)
weight = (num_samples[0]/num_samples[1]).round(2)

cols_to_scale = ['CreditScore', 'Age', 'Balance', 'EstimatedSalary',
                 'bal_per_product', 'bal_by_est_salary', 'tenure_age_ratio', 'age_surname_enc']


models = model_zoo()

X_train = df_train.drop(columns=['Exited'], axis=1)
X_val = df_val.drop(columns=['Exited'], axis=1)

X_train.shape, y_train.shape
X_val.shape, y_val.shape

'''search = RandomizedSearchCV(model, parameters, n_iter = 20, cv = 5, scoring = 'f1')
search.fit(X_train, y_train.ravel())
print(search.best_params_)
print(search.best_score_)
print(search.cv_results_)'''

grid = GridSearchCV(model, parameters, cv=5, scoring='f1', n_jobs=-1)
grid.fit(X_train, y_train.ravel())

X_train = df_train.drop(columns=['Exited'], axis=1)
X_val = df_val.drop(columns=['Exited'], axis=1)

lgb1 = LGBMClassifier(boosting_type='dart', class_weight={0: 1, 1: 1}, min_child_samples=20, n_jobs=- 1, importance_type='gain',
                      max_depth=4, num_leaves=31, colsample_bytree=0.6, learning_rate=0.1, n_estimators=21, reg_alpha=0, reg_lambda=0.5)


lgb2 = LGBMClassifier(boosting_type='dart', class_weight={0: 1, 1: 3.93}, min_child_samples=20, n_jobs=- 1, importance_type='gain',
                      max_depth=6, num_leaves=63, colsample_bytree=0.6, learning_rate=0.1, n_estimators=201, reg_alpha=1, reg_lambda=1)


lgb3 = LGBMClassifier(boosting_type='dart', class_weight={0: 1, 1: 3.0}, min_child_samples=20, n_jobs=- 1, importance_type='gain',
                      max_depth=6, num_leaves=63, colsample_bytree=0.6, learning_rate=0.1, n_estimators=201, reg_alpha=1, reg_lambda=1)


model_1 = Pipeline(steps=[('categorical_encoding', CategoricalEncoder()),
                          ('add_new_features', AddFeatures()),
                          ('classifier', lgb1)
                          ])

model_2 = Pipeline(steps=[('categorical_encoding', CategoricalEncoder()),
                          ('add_new_features', AddFeatures()),
                          ('classifier', lgb2)
                          ])

model_3 = Pipeline(steps=[('categorical_encoding', CategoricalEncoder()),
                          ('add_new_features', AddFeatures()),
                          ('classifier', lgb3)
                          ])


model_1.fit(X_train, y_train.ravel())
model_2.fit(X_train, y_train.ravel())
model_3.fit(X_train, y_train.ravel())


m1_pred_probs_trn = model_1.predict_proba(X_train)
m2_pred_probs_trn = model_2.predict_proba(X_train)
m3_pred_probs_trn = model_3.predict_proba(X_train)


df_t = pd.DataFrame(
    {'m1_pred': m1_pred_probs_trn[:, 1], 'm2_pred': m2_pred_probs_trn[:, 1], 'm3_pred': m3_pred_probs_trn[:, 1]})

m1_pred_probs_val = model_1.predict_proba(X_val)
m2_pred_probs_val = model_2.predict_proba(X_val)
m3_pred_probs_val = model_3.predict_proba(X_val)
threshold = 0.5

m3_preds = np.where(m3_pred_probs_val[:, 1] >= threshold, 1, 0)

m1_m2_preds = np.where(
    ((0.1*m1_pred_probs_val[:, 1]) + (0.9*m2_pred_probs_val[:, 1])) >= threshold, 1, 0)

roc = roc_auc_score(y_val, m3_preds)
recall = recall_score(y_val, m3_preds)
cf = confusion_matrix(y_val, m3_preds)

roc = roc_auc_score(y_val, m1_m2_preds)
recall = recall_score(y_val, m1_m2_preds)
cf = confusion_matrix(y_val, m1_m2_preds)

X_train = df_train.drop(columns=['Exited'], axis=1)
X_val = df_val.drop(columns=['Exited'], axis=1)

X_train.shape, y_train.shape
X_val.shape, y_val.shape

best_f1_lgb = L r(boosting_type='dart', class_weight={0: 1, 1: 3.0}, min_child_samples=20, n_jobs=- 1, importance_type='gain', max_depth=6, num_leaves=63, colsample_bytree=0.6, learning_rate=0.1, n_estimators=201, reg_alpha=1, reg_lambda=1)

best_recall_lgb = LGBMClassifier(boosting_type='dart', num_leaves=31, max_depth=6, learning_rate=0.1, n_estimators=21, class_weight={
                                 0: 1, 1: 3.93}, min_child_samples=2, colsample_bytree=0.6, reg_alpha=0.3, reg_lambda=1.0, n_jobs=- 1, importance_type='gain')


final_model = Pipeline(steps=[('categorical_encoding', CategoricalEncoder()),
                              ('add_new_features', AddFeatures()),
                              ('classifier', best_f1_lgb)
                              ])


final_model.fit(X_train, y_train)

val_probs = final_model.predict_proba(X_val)[:, 1]

val_preds = np.where(val_probs > 0.45, 1, 0)

roc_auc_score(y_val, val_preds)
recall_score(y_val, val_preds)
confusion_matrix(y_val, val_preds)

joblib.dump(final_model, '../output/final_churn_model_f1_0_45.sav')


model = joblib.load('../output/final_churn_model_f1_0_45.sav')

X_test = df_test.drop(columns=['Exited'], axis=1)
print(X_test.shape)
print(y_test.shape)

test_probs = model.predict_proba(X_test)[:, 1]

test_preds = np.where(test_probs > 0.45, 1, 0)

roc_auc_score(y_test, test_preds)
recall_score(y_test, test_preds)
confusion_matrix(y_test, test_preds)
print(classification_report(y_test, test_preds))

test = df_test.copy()
test['predictions'] = test_preds
test['pred_probabilities'] = test_probs

high_churn_list = test[test.pred_probabilities > 0.7].sort_values(by=['pred_probabilities'], ascending=False
                                                                  ).reset_index().drop(columns=['index', 'Exited', 'predictions'], axis=1)
print(high_churn_list.shape)
print(high_churn_list.head())
high_churn_list.to_csv('../output/high_churn_list.csv', index=False)

print("DONE")
