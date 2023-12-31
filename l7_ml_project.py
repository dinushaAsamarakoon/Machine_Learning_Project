# -*- coding: utf-8 -*-
"""l7-ml-project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18CEkYN1hStgUwQx0EsZpdkeBO1EQlzRG
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from catboost import CatBoostClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.decomposition import PCA
import seaborn as sn
from imblearn.over_sampling import RandomOverSampler
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import time
import os

import warnings
warnings.filterwarnings('ignore')

train = pd.read_csv('/kaggle/input/l7-data/train.csv')
valid = pd.read_csv('/kaggle/input/l7-data/valid.csv')
test = pd.read_csv('/kaggle/input/l7-data/test.csv')

train.head()

svm = SVC(kernel='linear')
def svm_classifier(X_train, Y_train, X_val, Y_val):
    svm.fit(X_train, Y_train)

    y_pred = svm.predict(X_val)

    accuracy = accuracy_score(Y_val, y_pred)
    return accuracy

knn = KNeighborsClassifier(n_neighbors=1)
def knn_classifier(X_train, Y_train, X_val, Y_val):

    knn.fit(np.array(X_train), Y_train)

    y_pred = knn.predict(np.array(X_val))

    accuracy = accuracy_score(Y_val, y_pred)
    return accuracy

logreg = LogisticRegression()
def logistic_regression_classifier(X_train, Y_train, X_val, Y_val):

    logreg.fit(X_train, Y_train)

    y_pred = logreg.predict(X_val)

    accuracy = accuracy_score(Y_val, y_pred)
    return accuracy

def id_highly_correlated_features(dataset, threshold):
    corr_matrix = dataset.corr().abs()
    upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool_))
    to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > threshold)]
    return set(to_drop)

def id_weekly_correlated_features_with_label(dataset, label, threshold = 0.01):
    for label_ in train.iloc[:, -4:]:
        if label_ != label:
            dataset = dataset.drop(label_, axis=1)  # remove other targets from the dataset
    corr_matrix = dataset.corr().abs()
    weak_corr_features = corr_matrix[corr_matrix[label] < threshold].index.tolist()
    if label in weak_corr_features:
        weak_corr_features.remove(label)
    return weak_corr_features

"""# **Label 1**"""

label_1_train = train.copy()
label_1_valid = valid.copy()
label_1_test = test.copy()

label_1_train = label_1_train.dropna(subset=['label_1'])
label_1_valid = label_1_valid.dropna(subset=['label_1'])

label_1_test.head()

X_train = label_1_train.iloc[:, :-4]
y_train = label_1_train.iloc[:, -4:]
X_val = label_1_valid.iloc[:, :-4]
y_val = label_1_valid.iloc[:, -4:]
X_test = label_1_test.iloc[:, 1:]

plt.figure(figsize=(18, 6))
sn.countplot(data=y_train, x='label_1', palette='Set2')
plt.title('Distribution of label_1 Classes')
plt.xlabel('label_1')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.show()

# accuracy with all the features
#svm
start_time = time.time()
accuracy = svm_classifier(X_train, y_train['label_1'], X_val, y_val['label_1'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

# accuracy with all the features
#knn
start_time = time.time()
accuracy = knn_classifier(X_train, y_train['label_1'], X_val, y_val['label_1'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

# accuracy with all the features
#logistic_regression_classifier
start_time = time.time()
accuracy = logistic_regression_classifier(X_train, y_train['label_1'], X_val, y_val['label_1'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

label_1_pred_before = svm.predict(np.array(X_test))

weekly_related_features = id_weekly_correlated_features_with_label(X_train_pca, 'label_1',0.01)
len(set(weekly_related_features))

print(f"dropping weekly related features count {len(set(weekly_related_features))}")
X_train_filtered = X_train.drop(columns=list(weekly_related_features))
X_val_filtered = X_val.drop(columns=list(weekly_related_features))
X_test_filtered = X_test.drop(columns=list(weekly_related_features))
start_time = time.time()
accuracy = svm_classifier(X_train_filtered, y_train['label_1'], X_val_filtered, y_val['label_1'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

highly_related_features = id_highly_correlated_features(X_train_filtered, 0.5)
len(set(highly_related_features))

print(f"dropping highly related features count {len(set(highly_related_features))}")
X_train_filtered = X_train_filtered.drop(columns=list(highly_related_features))
X_val_filtered = X_val_filtered.drop(columns=list(highly_related_features))
X_test_filtered = X_test_filtered.drop(columns=list(highly_related_features))
start_time = time.time()
accuracy = svm_classifier(X_train_filtered, y_train['label_1'], X_val_filtered, y_val['label_1'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_filtered)
X_val_scaled = scaler.transform(X_val_filtered)
X_test_scaled = scaler.transform(X_test_filtered)

start_time = time.time()
accuracy = svm_classifier(X_train_scaled, y_train['label_1'], X_val_scaled, y_val['label_1'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

X_train_scaled.shape

pca = PCA(n_components=0.95, svd_solver = 'full')
X_train_pca = pca.fit_transform(X_train)
X_val_pca = pca.transform(X_val)
X_test_pca = pca.transform(X_test)

start_time = time.time()
accuracy = svm_classifier(X_train_pca, y_train['label_1'], X_val_pca, y_val['label_1'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

X_train_pca.shape

# # Hyper Parameter Tuning For SVC

# from sklearn.model_selection import GridSearchCV

# # defining parameter range
# param_grid = {'C': [0.1, 1, 10, 100, 1000],
#               'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
#               'kernel': ['rbf']}

# grid = GridSearchCV(SVC(), param_grid, refit = True, verbose = 3)

# # fitting the model for grid search
# grid.fit(X_train_pca, y_train['label_1'])
# grid.best_params_

# grid.best_estimator_

cross_val_score(SVC(C=1000, gamma=0.001, kernel='rbf'), X_train_pca, y_train['label_1'], cv=3).mean()

best_model_label_1 = SVC(C=1000, gamma=0.001, kernel='rbf', probability=True)
best_model_label_1.fit(X_train_pca, y_train['label_1'])
pred = best_model_label_1.predict(X_val_pca)
accuracy_score(y_val['label_1'], pred )

label_1_pred_after = best_model_label_1.predict(np.array(X_test_pca))

"""Label 2"""

label_2_train = train.copy()
label_2_valid = valid.copy()
label_2_test = test.copy()
label_2_test.head()

label_2_train = label_2_train.dropna(subset=['label_2'])
label_2_valid = label_2_valid.dropna(subset=['label_2'])

X_train = label_2_train.iloc[:, :-4]
y_train = label_2_train.iloc[:, -3:]
X_val = label_2_valid.iloc[:, :-4]
y_val = label_2_valid.iloc[:, -3:]
X_test = label_2_test.iloc[:, 1:]

X_test.head()

plt.figure(figsize=(18, 6))
sn.histplot(data=y_train, x='label_2', bins=20, kde=False)

# accuracy with all the features
#svm
start_time = time.time()
accuracy = svm_classifier(X_train, y_train['label_2'], X_val, y_val['label_2'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

# accuracy with all the features
#knn
start_time = time.time()
accuracy = knn_classifier(X_train, y_train['label_2'], X_val, y_val['label_2'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

# accuracy with all the features
#logistic_regression_classifier
start_time = time.time()
accuracy = logistic_regression_classifier(X_train, y_train['label_2'], X_val, y_val['label_2'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

label_2_pred_before = svm.predict(np.array(X_test))

weekly_related_features = id_weekly_correlated_features_with_label(label_2_train, 'label_2')
print(f"dropping features count {len(set(weekly_related_features))}")

X_train_filtered = X_train.drop(columns=list(weekly_related_features))
X_val_filtered = X_val.drop(columns=list(weekly_related_features))
X_test_filtered = X_test.drop(columns=list(weekly_related_features))
start_time = time.time()
accuracy = svm_classifier(X_train_filtered, y_train['label_2'], X_val_filtered, y_val['label_2'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

highly_related_features = id_highly_correlated_features(X_train_filtered, 0.5)
print(f"dropping features count {len(set(highly_related_features))}")

X_train_filtered = X_train_filtered.drop(columns=list(highly_related_features))
X_val_filtered = X_val_filtered.drop(columns=list(highly_related_features))
X_test_filtered = X_test_filtered.drop(columns=list(highly_related_features))
start_time = time.time()
accuracy = svm_classifier(X_train_filtered, y_train['label_2'], X_val_filtered, y_val['label_2'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_filtered)
X_val_scaled = scaler.transform(X_val_filtered)
X_test_scaled = scaler.transform(X_test_filtered)

start_time = time.time()
accuracy = svm_classifier(X_train_scaled, y_train['label_2'], X_val_scaled, y_val['label_2'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

X_train_scaled.shape

pca = PCA(n_components=0.95, svd_solver = 'full')
X_train_pca = pca.fit_transform(X_train_scaled)
X_val_pca = pca.transform(X_val_scaled)
X_test_pca = pca.transform(X_test_scaled)

start_time = time.time()
accuracy = svm_classifier(X_train_pca, y_train['label_2'], X_val_pca, y_val['label_2'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

X_train_pca.shape

X_test_pca.shape

# from sklearn.model_selection import GridSearchCV

# # defining parameter range
# param_grid = {'C': [1000, 1200, 1300, 1500, 1600, 2000, 1800, 2200],
#               'kernel': ['rbf']}

# grid = GridSearchCV(SVC(), param_grid, refit = True, verbose = 3)

# # fitting the model for grid search
# grid.fit(X_train_pca, y_train['label_2'])
# grid.best_params_

cross_val_score(SVC(C=1000, kernel='rbf'), X_train_pca, y_train['label_2'], cv=5).mean()

best_model_label_2 = SVC(C=1000, kernel='rbf')
best_model_label_2.fit(X_train_pca, y_train['label_2'])
pred = best_model_label_2.predict(X_val_pca)
accuracy_score(y_val['label_2'], pred )

label_2_pred_after = best_model_label_2.predict(np.array(X_test_pca))

"""Label 3"""

label_3_train = train.copy()
label_3_valid = valid.copy()
label_3_test = test.copy()

label_3_train = label_3_train.dropna(subset=['label_3'])
label_3_valid = label_3_valid.dropna(subset=['label_3'])

X_train = label_3_train.iloc[:, :-4]
y_train = label_3_train.iloc[:, -2:]
X_val = label_3_valid.iloc[:, :-4]
y_val = label_3_valid.iloc[:, -2:]
X_test = label_3_test.iloc[:, 1:]

plt.figure(figsize=(18, 6))
sn.histplot(data=y_train, x='label_3', bins=20, kde=False)

ros = RandomOverSampler(random_state=0, sampling_strategy=0.75)
X_train_resampled, y_train_resampled = ros.fit_resample(X_train, y_train['label_3'])

y_train_resampled

ax = sn.countplot(x=y_train['label_3'])

for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='bottom', fontsize=9, color='black')

# accuracy with all the features
#svm
start_time = time.time()
accuracy = svm_classifier(X_train_resampled, y_train_resampled, X_val, y_val['label_3'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

# accuracy with all the features
#knn
start_time = time.time()
accuracy = knn_classifier(X_train_resampled, y_train_resampled, X_val, y_val['label_3'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

# accuracy with all the features
#logistic_regression_classifier
start_time = time.time()
accuracy = logistic_regression_classifier(X_train_resampled, y_train_resampled, X_val, y_val['label_3'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

label_3_pred_before = svm.predict(np.array(X_test))

weekly_related_features = id_weekly_correlated_features_with_label(label_3_train, 'label_3',0.03)
print(f"dropping features count {len(set(weekly_related_features))}")

X_train_filtered = X_train_resampled.drop(columns=list(weekly_related_features))
X_val_filtered = X_val.drop(columns=list(weekly_related_features))
X_test_filtered = X_test.drop(columns=list(weekly_related_features))
start_time = time.time()
accuracy = svm_classifier(X_train_filtered, y_train_resampled, X_val_filtered, y_val['label_3'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

highly_related_features = id_highly_correlated_features(X_train_filtered, 0.5)
print(f"dropping features count {len(set(highly_related_features))}")

X_train_filtered = X_train_filtered.drop(columns=list(highly_related_features))
X_val_filtered = X_val_filtered.drop(columns=list(highly_related_features))
X_test_filtered = X_test_filtered.drop(columns=list(highly_related_features))
start_time = time.time()
accuracy = svm_classifier(X_train_filtered, y_train_resampled, X_val_filtered, y_val['label_3'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_filtered)
X_val_scaled = scaler.transform(X_val_filtered)
X_test_scaled = scaler.transform(X_test_filtered)

X_train_scaled.shape

start_time = time.time()
accuracy = svm_classifier(X_train_scaled, y_train_resampled, X_val_scaled, y_val['label_3'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

pca = PCA(n_components=0.95, svd_solver = 'full')
X_train_pca = pca.fit_transform(X_train_scaled)
X_val_pca = pca.transform(X_val_scaled)
X_test_pca = pca.transform(X_test_scaled)

start_time = time.time()
accuracy = svm_classifier(X_train_pca, y_train_resampled, X_val_pca, y_val['label_3'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

cross_val_score(SVC(), X_train_pca, y_train['label_3'], cv=5).mean()

best_model_label_3 = SVC()
label_3_pred_after = best_model_label_3.fit(X_train_pca, y_train['label_3']).predict(np.array(X_test_pca))

"""Label 4"""

label_4_train = train.copy()
label_4_valid = valid.copy()
label_4_test = test.copy()

label_4_train = label_4_train.dropna(subset=['label_4'])
label_4_valid = label_4_valid.dropna(subset=['label_4'])

X_train = label_4_train.iloc[:, :-4]
y_train = label_4_train.iloc[:, -1:]
X_val = label_4_valid.iloc[:, :-4]
y_val = label_4_valid.iloc[:, -1:]
X_test = label_4_test.iloc[:, 1:]

plt.figure(figsize=(18, 6))
sn.histplot(data=y_train, x='label_4', bins=20, kde=False)

plt.figure(figsize=(18, 6))
ax = sn.countplot(x=y_train['label_4'], color='teal')

for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='bottom', fontsize=9, color='black')

# accuracy with all the features
#knn
start_time = time.time()
accuracy = knn_classifier(X_train, y_train, X_val, y_val['label_4'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

label_4_pred_before = knn.predict(np.array(X_test))

ros = RandomOverSampler(random_state=0)
X_train_resampled, y_train_resampled = ros.fit_resample(X_train, y_train['label_4'])

plt.figure(figsize=(18, 6))
ax = sn.countplot(x=y_train_resampled, color='teal')

for p in ax.patches:
    ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='bottom', fontsize=9, color='black')

# accuracy with all the features
#svm
start_time = time.time()
accuracy = svm_classifier(X_train_resampled, y_train_resampled, X_val, y_val['label_4'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

# accuracy with all the features
#knn
start_time = time.time()
accuracy = knn_classifier(X_train_resampled, y_train_resampled, X_val, y_val['label_4'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

# accuracy with all the features
#logistic_regression_classifier
start_time = time.time()
accuracy = logistic_regression_classifier(X_train_resampled, y_train_resampled, X_val, y_val['label_4'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

label_4_pred_before = svm.predict(np.array(X_test))

weekly_related_features = id_weekly_correlated_features_with_label(label_4_train, 'label_4', 0.01)
print(f"dropping features count {len(set(weekly_related_features))}")

X_train_filtered = X_train_resampled.drop(columns=list(weekly_related_features))
X_val_filtered = X_val.drop(columns=list(weekly_related_features))
X_test_filtered = X_test.drop(columns=list(weekly_related_features))
start_time = time.time()
accuracy = svm_classifier(X_train_filtered, y_train_resampled, X_val_filtered, y_val['label_4'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

highly_related_features = id_highly_correlated_features(X_train_filtered, 0.5)
print(f"dropping features count {len(set(highly_related_features))}")

X_train_filtered = X_train_filtered.drop(columns=list(highly_related_features))
X_val_filtered = X_val_filtered.drop(columns=list(highly_related_features))
X_test_filtered = X_test_filtered.drop(columns=list(highly_related_features))
start_time = time.time()
accuracy = svm_classifier(X_train_filtered, y_train_resampled, X_val_filtered, y_val['label_4'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_filtered)
X_val_scaled = scaler.transform(X_val_filtered)
X_test_scaled = scaler.transform(X_test_filtered)

X_train_scaled.shape

start_time = time.time()
accuracy = svm_classifier(X_train_filtered, y_train_resampled, X_val_filtered, y_val['label_4'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

pca = PCA(n_components=0.95, svd_solver = 'full')
X_train_pca = pca.fit_transform(X_train_scaled)
X_val_pca = pca.transform(X_val_scaled)
X_test_pca = pca.transform(X_test_scaled)

X_train_pca.shape

start_time = time.time()
accuracy = svm_classifier(X_train_pca, y_train_resampled, X_val_pca, y_val['label_4'] )
elapsed_time = time.time() - start_time
print(f"Accuracy: {accuracy * 100:.2f}% in {elapsed_time} secs")

# from sklearn.model_selection import GridSearchCV

# # defining parameter range
# param_grid = {'C': [1000, 1200, 1300, 1500, 1600, 2000, 1800, 2200],
#               'class_weight': ['balanced', None]}

# grid = GridSearchCV(SVC(), param_grid, refit = True, verbose = 3)

# # fitting the model for grid search
# grid.fit(X_train_pca, y_train['label_2'])
# grid.best_params_

cross_val_score(SVC(class_weight='balanced', C=1000), X_train_pca, y_train['label_4'], cv=5, scoring='accuracy').mean()

best_model_label_4 = SVC(class_weight='balanced', C=1000)

label_4_pred_after = best_model_label_4.fit(X_train_pca, y_train['label_4']).predict(X_test_pca)

"""Kaggle competition output"""

output_df = test[['ID']]
output_df['label_1'] = label_1_pred_after
output_df['label_2'] = label_2_pred_after
output_df['label_3'] = label_3_pred_after
output_df['label_4'] = label_4_pred_after

output_df.head()

# Write DataFrame to CSV
output_df.to_csv('predictions_L7.csv', index=False)