import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
import joblib


df = pd.read_csv('questions.csv', header=0)

labels = df['intent']
text = df['text']

X_train, X_test, y_train, y_test = train_test_split(text, labels, random_state=0, test_size=0.3)

count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
tf_transformer = TfidfTransformer().fit(X_train_counts)
X_train_transformed = tf_transformer.transform(X_train_counts)

X_test_counts = count_vect.transform(X_test)
X_test_transformed = tf_transformer.transform(X_test_counts)

labels = LabelEncoder()
y_train_labels_fit = labels.fit(y_train)
y_train_lables_trf = labels.transform(y_train)

print(labels.classes_)

linear_svc = LinearSVC()
clf = linear_svc.fit(X_train_transformed, y_train_lables_trf)

calibrated_svc = CalibratedClassifierCV(base_estimator=linear_svc,
                                        cv="prefit")

calibrated_svc.fit(X_train_transformed, y_train_lables_trf)
predicted = calibrated_svc.predict(X_test_transformed)

to_predict = [
    "what is there to shop here"]
p_count = count_vect.transform(to_predict)
p_tfidf = tf_transformer.transform(p_count)
print('Average accuracy on test set={}'.format(np.mean(predicted == labels.transform(y_test))))
print('Predicted probabilities of demo input string are')
print(calibrated_svc.predict_proba(p_tfidf))

print(pd.DataFrame(calibrated_svc.predict_proba(p_tfidf)*100, columns=labels.classes_))

# Output a pickle file for the model
joblib.dump(calibrated_svc, 'intent_classification.pkl')
joblib.dump(tf_transformer, 'tf_transformer.pkl')
joblib.dump(count_vect, 'count_vect.pkl')
