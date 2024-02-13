import numpy as np
import joblib


def predict(df):
    try:
        cols_to_remove = ['RowNumber', 'CustomerId']
        if 'Exited' in list(df.columns):
            df.drop(columns=['Exited'], axis=1, inplace=True)
        for col in cols_to_remove:
            if col in list(df.columns):
                df.drop(cols_to_remove, axis=1, inplace=True)
        model = joblib.load('../output/final_churn_model_f1_0_45.sav')
        test_probs = model.predict_proba(df)[:, 1]
        test_preds = np.where(test_probs > 0.45, 1, 0)

        test = df.copy()
        test['predictions'] = test_preds
        test['pred_probabilities'] = test_probs

        high_churn_list = test[test.pred_probabilities > 0.7].sort_values(by=['pred_probabilities'], ascending=False
                                                                          ).reset_index().drop(columns=['index', 'predictions'], axis=1)
        print(high_churn_list.shape)
        print(high_churn_list.head())

        return 200, high_churn_list
    except Exception as error:
        return 500, str(error)
